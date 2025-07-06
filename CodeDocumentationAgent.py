from CodeGraphReaderTool import CodeGraphReaderTool


class CodeDocumentationAgent:
    def SetCodeDocumentationAgent(llm,Agent, graph_summary):
        return Agent(
        role="Software Documentation Generator",
        goal="Generate high-quality Markdown documentation using knowledge of code and its relationships from Graph Summary",
        backstory=f"""You are an AI engineer trained to write clean, modular, human-readable documentation
        for C# codebases. You understand class responsibilities, call relationships, and inheritance,
        and produce linked .md documentation that includes usage context and diagrams. Here is the Graph Summary: {graph_summary}.
        This Graph Summary should be considered while generating document""",
        llm=llm,
        allow_delegation=False,
        verbose=True
    )
    def SetCodeDocumentationPlan (Agent, Task):
        return Task(
        description=f"""For each class or module in the codebase, analyze the provided knowledge graph to find 
        its related components (e.g., calls, inheritance). Use this information to write a single Markdown file 
        that explains the purpose of the classes, its methods, and how it interacts with others.""",
        expected_output=f"""One well-structured Markdown doc with Mermaid diagrams if applicable.""",
        agent=Agent
        )