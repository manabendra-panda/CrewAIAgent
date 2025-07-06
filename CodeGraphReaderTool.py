from typing import Optional
from crewai_tools import BaseTool
from pydantic import BaseModel
from typing import List, Dict, Any, Type
import json


class CodeGraphReaderTool(BaseTool):
    name: str = "CodeGraphReaderTool"
    description: str = ("Reads a knowledge graph from C# code and returns related entities for a given class/module.")

    def _run(self, class_name: str, graph : Any = None) -> str:
        if not graph:
            return "❌ Missing 'graph' input."
    
        # Convert stringified JSON to dict if needed
        if isinstance(graph, str):
            try:
                graph = json.loads(graph)
            except json.JSONDecodeError as e:
                return f"\u26a0\ufe0f Failed to parse graph JSON: {e}"
            
        # Validate the expected keys
        if not isinstance(graph, dict) or "edges" not in graph:
            return "\u26a0\ufe0f Invalid graph input. Expected a dict with an 'edges' key."
        
        related = []
        for edge in graph["edges"]:
            if edge["source"] == class_name or edge["target"] == class_name:
                related.append(f'{edge["source"]} --[{edge["type"]}]--> {edge["target"]}')
        
        if not related:
            return f"No relationships found for {class_name}"
        
        return f"Relationships for {class_name}:\n" + "\n".join(related)