from typing import Dict, List, Set

class ResourceAllocationGraph:
    """
    Implements Resource Allocation Graph (RAG) and Circular Dependency
    Deadlock Detection for Worker Processes.
    Nodes: Workers (e.g., Worker-1) and System Resources (e.g., CPU, Memory_Chunk_A).
    Edges: Resource Requests (Worker -> Resource) and Allocations (Resource -> Worker).
    """

    def __init__(self):
        self.edges: Dict[str, List[str]] = {}

    def add_edge(self, u: str, v: str):
        """Adds directed edge from u to v."""
        if u not in self.edges:
            self.edges[u] = []
        if v not in self.edges[u]:
            self.edges[u].append(v)

    def remove_edge(self, u: str, v: str):
        """Removes directed edge from u to v."""
        if u in self.edges and v in self.edges[u]:
            self.edges[u].remove(v)

    def clear(self):
        self.edges.clear()

    def detect_deadlock(self) -> tuple[bool, List[str]]:
        """
        Uses DFS to detect cycles in the directed Graph.
        Returns (has_deadlock: bool, cycle_path: List[str]).
        """
        visited: Set[str] = set()
        rec_stack: Set[str] = set()
        cycle_path: List[str] = []

        def dfs(node: str, path: List[str]) -> bool:
            visited.add(node)
            rec_stack.add(node)
            path.append(node)

            for neighbor in self.edges.get(node, []):
                if neighbor not in visited:
                    if dfs(neighbor, path):
                        return True
                elif neighbor in rec_stack:
                    path.append(neighbor)
                    cycle_path.extend(path)
                    return True

            path.pop()
            rec_stack.remove(node)
            return False

        for node in list(self.edges.keys()):
            if node not in visited:
                if dfs(node, []):
                    return True, cycle_path

        return False, []

# Global RAG Instance
rag = ResourceAllocationGraph()

