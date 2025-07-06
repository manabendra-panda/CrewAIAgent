# Introduction 
TODO: A Python-based tool for automatically generating documentation from C# code repositories. 

# 🚀 Getting Started
TODO: This project uses Python and CrewAI to automatically generate documentation from a C# codebase, representing it as a knowledge graph and converting relationships into Markdown documentation.
## 📦 Prerequisites
Make sure the following are installed:
- Python 3.12.0
- Git
- pip 25.1.1
- [Azure DevOps PAT](https://learn.microsoft.com/en-us/azure/devops/organizations/accounts/use-personal-access-tokens-to-authenticate)

## 🔧 Installation

```bash
# Clone the repository
git clone https://github.com/manabendra-panda/CrewAIAgent.git
cd CrewAIAgent.git

# Set up virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

##🔐 Environment Variables
AZURE_OPENAI_API_KEY={AZURE_OPENAI_API_KEY}
AZURE_OPENAI_API_VERSION={AZURE_OPENAI_API_VERSION}
AZURE_OPENAI_ENDPOINT={AZURE_OPENAI_ENDPOINT}
AZURE_OPENAI_DEPLOYMENT={AZURE_OPENAI_DEPLOYMENT}
AZURE_DEVOPS_PAT = {AZURE_DEVOPS_PAT}
AZURE_DEVOPS_ORG = {AZURE_DEVOPS_ORG}
AZURE_DEVOPS_PROJECT = {AZURE_DEVOPS_PROJECT}
AZURE_DEVOPS_REPOSITORY = {AZURE_DEVOPS_REPOSITORY}
AZURE_DEVOPS_BRANCH = {AZURE_DEVOPS_BRANCH}

## 🧠 Run the Agent Crew
Execute the main agent script:
```bash
python Code.py

## 📁 Project Structure
```
├── Code.py                    # Main entry script
├── CodeDocumentationAgent.py # Defines the CrewAI agent
├── KnowledgeGraphBuilder.py  # Parses C# and builds graph
├── requirements.txt
└── README.md

# Contribute
TODO: Explain how other users and developers can contribute to make your code better. 


