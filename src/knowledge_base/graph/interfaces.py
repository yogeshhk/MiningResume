from typing import Protocol, Dict, Any, List


class GraphStore(Protocol):
    def upsert_node(self, label: str, properties: Dict[str, Any]) -> Any: ...
    def upsert_edge(
        self,
        src_id: Any,
        rel_type: str,
        dst_id: Any,
        properties: Dict[str, Any] | None = None,
    ) -> Any: ...
    def query(self, cypher: str, params: Dict[str, Any] | None = None) -> List[Dict]: ...