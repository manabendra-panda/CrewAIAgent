import re
from typing import Dict, List
import networkx as nx

class KnowledgeGraphBuilder:
    def build_code_knowledge_graph_from_csharp(file_contents) -> Dict:
        
        nodes = []
        edges = []

        class_pattern = re.compile(r'class\s+(\w+)(?:\s*:\s*(\w+))?')
        method_pattern = re.compile(r'(?:public|private|protected|internal)?\s*(?:async\s+)?(?:\w+<\w+>|\w+)\s+(\w+)\s*\(')
        call_pattern = re.compile(r'(\w+)\s*\.\s*\w+\s*\(')  # matches calls like Helper.Method(

        for path, code in file_contents:
            filename = path
            code = code
            current_class = None
            lines = code.split('\n')

            for line in lines:
                # Match class and inheritance
                class_match = class_pattern.search(line)
                if class_match:
                    class_name = class_match.group(1)
                    base_class = class_match.group(2)
                    current_class = class_name

                    nodes.append({"id": class_name, "type": "class", "file": filename})

                    if base_class:
                        edges.append({"source": class_name, "target": base_class, "type": "inherits"})

                # Match method
                method_match = method_pattern.search(line)
                if method_match and current_class:
                    method_name = method_match.group(1)
                    full_method_id = f"{current_class}.{method_name}"
                    nodes.append({"id": full_method_id, "type": "method", "parent": current_class})
                    edges.append({"source": current_class, "target": full_method_id, "type": "defines"})

                # Match usage (simple dot call)
                call_match = call_pattern.findall(line)
                if call_match and current_class:
                    for called_class in call_match:
                        if called_class != current_class:
                            edges.append({"source": current_class, "target": called_class, "type": "uses"})

        return {"nodes": nodes, "edges": edges}
    
    def convert_to_networkx(graph_dict: Dict) -> nx.DiGraph:
        """
        Convert the graph dictionary to a NetworkX directed graph.

        Args:
            graph_dict: Dictionary with 'nodes' and 'edges'.

        Returns:
            NetworkX DiGraph.
        """
        G = nx.DiGraph()

        for node in graph_dict["nodes"]:
            G.add_node(node["id"], **node)

        for edge in graph_dict["edges"]:
            G.add_edge(edge["source"], edge["target"], type=edge["type"])

        return G
