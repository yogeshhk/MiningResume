# knowledge_base

**Status: experimental / nascent**

This module bridges the resume parser output with a Neo4j graph database. It is not yet wired into the main pipeline and is intended for future exploration of graph-based resume analysis (e.g. skill similarity, career path matching).

## Components

| File | Purpose |
|------|---------|
| `graph/interfaces.py` | `GraphStore` abstract interface — defines `upsert_node` and `upsert_edge` |
| `graph/neo4j_store.py` | Neo4j implementation of `GraphStore` using the `neo4j` driver |
| `graph/graph_builder.py` | Takes an `ExtractedResume`-shaped dict and writes Person, Skill, Employment, Education, Project, and Accomplishment nodes/edges into the store |

## Graph schema

```
(Person)-[:HAS_SKILL]->(Skill)
(Person)-[:HAS_EMPLOYMENT]->(Employment)
(Person)-[:HAS_EDUCATION]->(Education)
(Person)-[:WORKED_ON]->(Project)
(Person)-[:HAS_ACCOMPLISHMENT]->(Accomplishment)
```

## Prerequisites

- A running Neo4j instance (default: `bolt://localhost:7687`)
- Set `NEO4J_URI`, `NEO4J_USERNAME`, `NEO4J_PASSWORD` in your `.env` file

## Example usage

```python
from src.knowledge_base.graph.neo4j_store import Neo4jStore
from src.knowledge_base.graph.graph_builder import build_graph
from src.llm_based.config.settings import settings

store = Neo4jStore(settings.neo4j_uri, settings.neo4j_username, settings.neo4j_password)
build_graph(store, parser_result.extracted_data.model_dump())
store.close()
```
