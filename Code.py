# Warning control
import warnings
from langchain_openai import AzureChatOpenAI

warnings.filterwarnings('ignore')

# importing knowledge graph
import re
import networkx as nx
import requests

#import custom agents
from CodeDocumentationAgent import CodeDocumentationAgent

#import Knowledge graph builder
from KnowledgeGraphBuilder import KnowledgeGraphBuilder 
from CodeGraphReaderTool import CodeGraphReaderTool

#Azure Devops import
from azure.devops.connection import Connection
from azure.devops.v7_0.git.models import GitVersionDescriptor
from msrest.authentication import BasicAuthentication


from dotenv import load_dotenv
from openai import AsyncAzureOpenAI

from crewai import Agent, Task, Crew
from IPython.display import Markdown
import os

load_dotenv()
#Create OpenAI client using Azure OpenAI
llm = AzureChatOpenAI(
    api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    deployment_name=os.getenv("AZURE_OPENAI_DEPLOYMENT")
)

#create Azure DevOps connection using PAT token
organizationName = os.getenv("AZURE_DEVOPS_ORG")
organizationUrl = f"https://dev.azure.com/{organizationName}/"
projectName = os.getenv("AZURE_DEVOPS_PROJECT")
repositoryName = os.getenv("AZURE_DEVOPS_REPOSITORY")
branchName=os.getenv("AZURE_DEVOPS_BRANCH")
filePath= "/README_Agentic.md"
personalAccessToken = os.getenv("AZURE_DEVOPS_PAT") 

patCredential = BasicAuthentication("", personalAccessToken)
orgConnection = Connection(base_url=organizationUrl, creds=patCredential)

#access git client
git_client = orgConnection.clients.get_git_client()

# List items (files/folders) recursively
def get_files_recursively(path='/', collected=None):
    if collected is None:
        collected = []

    versionDescriptor = GitVersionDescriptor()
    versionDescriptor.version = branchName
    versionDescriptor.version_type = 'branch'

    items = git_client.get_items(
        repository_id=repositoryName,
        project=projectName,
        scope_path= path,
        recursion_level='Full',
        version_descriptor= versionDescriptor
    )

    for item in items:
        if item.is_folder:
            continue
        if item.path.endswith('.cs'):
            content = git_client.get_item_content(
                repository_id=repositoryName,
                path=item.path,
                project=projectName,
                version_type = 'branch',
                version= branchName,
                include_content=True
            )
            codeBytes = b"".join(content)
            try:
                code = codeBytes.decode('utf-8')
            except UnicodeDecodeError:
                code = codeBytes.decode('cp1252')
            collected.append((item.path, code))

    return collected

#build knowledge graph
def build_graph(codeFiles):
    graph = nx.DiGraph()
    for path, code in codeFiles:
        extract_structure_from_code(code, path, graph)
    return graph

def extract_structure_from_code(code, filename, graph):
    classes = re.findall(r'\bclass\s+(\w+)', code)
    methods = re.findall(r'\b(public|private|protected|internal)\s+\w[\w<>]*\s+(\w+)\s*\(.*?\)', code)

    for cls in classes:
        graph.add_node(cls, type='class', file=filename)
        graph.add_edge(filename, cls, relation='defines')

    for _, method in methods:
        graph.add_node(method, type='method', file=filename)
        graph.add_edge(filename, method, relation='defines')

    return graph

def graph_to_text(graph):
    lines = []
    for node, attrs in graph.nodes(data=True):
        if attrs.get('type') in ['class', 'method']:
            lines.append(f"{attrs['type'].title()}: `{node}` in `{attrs['file']}`")
    return "\n".join(lines)

def generate_documentation(graph_summary):
    #Code Documentation Agent
    codeDocumentationAgent = CodeDocumentationAgent.SetCodeDocumentationAgent(llm, Agent, graph_summary)

    #Code Documentation Plan
    codeDocumentationPlan = CodeDocumentationAgent.SetCodeDocumentationPlan(codeDocumentationAgent, Task)

    #starting execution
    crew = Crew(
    agents=[codeDocumentationAgent],
    tasks=[codeDocumentationPlan],
    verbose= True
    )
    return crew.kickoff()

# list of code files
codeFiles = get_files_recursively('/')
# graph = KnowledgeGraphBuilder.build_code_knowledge_graph_from_csharp(codeFiles)
# print(graph)
# tool = CodeGraphReaderTool()
graph = build_graph(codeFiles)
graph_summary = graph_to_text(graph)
documentation = generate_documentation(graph_summary)

#commit to git repository

#1.  Setup REST headers
base_url = f"https://dev.azure.com/{organizationName}"
auth = requests.auth.HTTPBasicAuth("", personalAccessToken)
headers = {"Content-Type": "application/json"}

# 1. Get latest commit ID from branch
ref_url = f"{base_url}/{projectName}/_apis/git/repositories/{repositoryName}/refs?filter=heads/{branchName}&api-version=7.0"
ref_resp = requests.get(ref_url, auth=auth)
ref_data = ref_resp.json()
if not ref_data["value"]:
    raise Exception(f"Branch '{branchName}' not found.")
latest_commit_id = ref_data["value"][0]["objectId"]

# 2. Check if file exist
file_check_url = f"{base_url}/{projectName}/_apis/git/repositories/{repositoryName}/items?path={filePath}&versionDescriptor.version={branchName}&includeContentMetadata=false&api-version=7.0"
file_check = requests.get(file_check_url, auth=auth)
change_type = "edit" if file_check.status_code == 200 else "add"

# 3. Prepare push payload
push_url = f"{base_url}/{projectName}/_apis/git/repositories/{repositoryName}/pushes?api-version=7.0"

push_payload = {
    "refUpdates": [{
        "name": f"refs/heads/{branchName}",
        "oldObjectId": latest_commit_id
    }],
    "commits": [{
        "comment": "📘 Auto-generate documentation",
        "changes": [{
            "changeType": change_type,  
            "item": {
                "path": filePath
            },
            "newContent": {
                "content": documentation,
                "contentType": "rawtext"
            }
        }]
    }]
}

# 4. Send push request
resp = requests.post(push_url, json=push_payload, headers=headers, auth=auth)

if resp.status_code == 201:
    print("✅ Push successful!")
else:
    print(f"❌ Push failed! {resp.status_code} - {resp.text}")
