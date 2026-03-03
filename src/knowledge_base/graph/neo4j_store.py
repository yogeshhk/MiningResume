from typing import Dict, Any, List
from neo4j import GraphDatabase
from .interfaces import GraphStore


class Neo4jStore(GraphStore):

    def __init__(self, uri: str, user: str, password: str):
        self._driver = GraphDatabase.driver(uri, auth=(user, password))

    def upsert_node(self, label: str, properties: Dict[str, Any]) -> Any:
        query = f"""
        MERGE (n:{label} {{id: $id}})
        SET n += $properties
        RETURN id(n) as node_id
        """
        with self._driver.session() as session:
            result = session.run(
                query,
                {
                    "id": properties.get("id"),
                    "properties": properties,
                },
            )
            return result.single()["node_id"]

    def upsert_edge(
        self,
        src_id: Any,
        rel_type: str,
        dst_id: Any,
        properties: Dict[str, Any] | None = None,
    ) -> Any:
        query = f"""
        MATCH (a), (b)
        WHERE id(a) = $src_id AND id(b) = $dst_id
        MERGE (a)-[r:{rel_type}]->(b)
        SET r += $properties
        RETURN id(r) as rel_id
        """
        with self._driver.session() as session:
            result = session.run(
                query,
                {
                    "src_id": src_id,
                    "dst_id": dst_id,
                    "properties": properties or {},
                },
            )
            return result.single()["rel_id"]

    def query(self, cypher: str, params: Dict[str, Any] | None = None) -> List[Dict]:
        with self._driver.session() as session:
            result = session.run(cypher, params or {})
            return [record.data() for record in result]