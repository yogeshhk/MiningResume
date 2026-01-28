from typing import Dict, Any
from neo4j import GraphDatabase
from src.llm_based.config.settings import settings
import json
import re


# Split helpers (LLM-safe)

def split_skills(text: str):
    return [s.strip() for s in text.split(",") if s.strip()]


def split_employment(text: str):
    parts = re.split(r"•|\n{2,}", text)
    return [p.strip() for p in parts if len(p.strip()) > 25]


def split_education(text: str):
    parts = re.split(r"(Bachelor|Master|Associate|PhD)", text)
    merged = []
    for i in range(1, len(parts), 2):
        merged.append(parts[i] + parts[i + 1])
    return [m.strip() for m in merged]


def split_projects(text: str):
    parts = re.split(r"•|\n", text)
    return [p.strip() for p in parts if len(p.strip()) > 20]

# Config

PERSON_PROPS = {"name", "email", "phone_number", "address"}

RELATIONSHIP_MAPPING = {
    "skills": ("Skill", "HAS_SKILL", split_skills),
    "employment_history": ("Employment", "WORKED_AT", split_employment),
    "education_history": ("Education", "STUDIED_AT", split_education),
    "projects": ("Project", "WORKED_ON", split_projects),
    "accomplishments": ("Accomplishment", "ACHIEVED", lambda x: [x]),
    "objective": ("Objective", "HAS_OBJECTIVE", lambda x: [x]),
}

# Neo4j Service

class Neo4jService:
    """Service to handle Neo4j operations: upsert, delete, query."""

    def __init__(self):
        self.driver = GraphDatabase.driver(
            settings.neo4j_uri,
            auth=(settings.neo4j_username, settings.neo4j_password)
        )

    def close(self):
        self.driver.close()

    def delete_resume_graph(self, filename: str = None):
        """Delete Person nodes by filename or entire graph."""
        with self.driver.session() as session:
            if filename:
                session.run(
                    """
                    MATCH (p:Person {filename: $filename})
                    DETACH DELETE p
                    """,
                    filename=filename
                )
            else:
                session.run("MATCH (n) DETACH DELETE n")

    def upsert_resume_graph(self, resume_json: Dict[str, Any], overwrite: bool = True):
        """
        Create / update Person node.
        - Basic identity fields as properties
        - Complex fields as relationship nodes (multi-node supported)
        """

        # Defensive: accept JSON string or dict
        if isinstance(resume_json, str):
            resume_json = json.loads(resume_json)

        filename = resume_json.get("filename")
        attributes = resume_json.get("extracted_attributes", {})

        person_name = attributes.get("name")
        if not person_name:
            raise ValueError("Person name is required")

        if overwrite:
            self.delete_resume_graph(filename)

        with self.driver.session() as session:
            # -----------------------------
            # 1️⃣ Create / update Person
            # -----------------------------
            session.run(
                """
                MERGE (p:Person {name: $name})
                SET p.filename = $filename,
                    p.email = $email,
                    p.phone_number = $phone_number,
                    p.address = $address
                """,
                {
                    "name": person_name,
                    "filename": filename,
                    "email": attributes.get("email"),
                    "phone_number": attributes.get("phone_number"),
                    "address": attributes.get("address"),
                }
            )

            # -----------------------------
            # 2️⃣ Create relationships
            # -----------------------------
            for field, value in attributes.items():
                if not value or field in PERSON_PROPS:
                    continue

                if field not in RELATIONSHIP_MAPPING:
                    continue

                node_label, rel_type, splitter = RELATIONSHIP_MAPPING[field]
                items = splitter(value)

                for item in items:
                    session.run(
                        f"""
                        MATCH (p:Person {{name: $name}})
                        MERGE (n:{node_label} {{value: $value}})
                        MERGE (p)-[:{rel_type}]->(n)
                        """,
                        {
                            "name": person_name,
                            "value": item
                        }
                    )

    def query_graph(self, cypher_query: str):
        """Run a custom Cypher query and return results."""
        with self.driver.session() as session:
            result = session.run(cypher_query)
            return [dict(record) for record in result]

    def get_full_graph(self):
        """Return all nodes and edges for visualization / chatbot context."""
        with self.driver.session() as session:
            result = session.run(
                """
                MATCH (n)
                OPTIONAL MATCH (n)-[r]->(m)
                RETURN n, r, m
                """
            )

            nodes = {}
            edges = []

            for record in result:
                n = record["n"]
                r = record["r"]
                m = record["m"]

                nodes[n.id] = {
                    "id": str(n.id),
                    "label": list(n.labels)[0] if n.labels else "Node",
                    "properties": dict(n)
                }

                if r and m:
                    nodes[m.id] = {
                        "id": str(m.id),
                        "label": list(m.labels)[0] if m.labels else "Node",
                        "properties": dict(m)
                    }
                    edges.append({
                        "from": str(n.id),
                        "to": str(m.id),
                        "type": r.type
                    })

            return {"nodes": list(nodes.values()), "edges": edges}
