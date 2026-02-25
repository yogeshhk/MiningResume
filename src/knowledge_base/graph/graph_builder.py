from typing import Dict, Any
from .interfaces import GraphStore


def build_graph(store: GraphStore, entities: Dict[str, Any]) -> None:
    extracted = entities.get("extracted_attributes", {})

    name = extracted.get("name")
    if not name:
        print("No name found. Skipping.")
        return

    # ---- Create Person ----
    person_id = store.upsert_node(
        "Person",
        {
            "id": name,
            "name": name,
            "email": extracted.get("email"),
            "phone_number": extracted.get("phone_number"),
            "address": extracted.get("address"),
            "objective": extracted.get("objective"),
        },
    )

    # ---- Skills ----
    skills_raw = extracted.get("skills", "")
    skills = [s.strip() for s in skills_raw.split(",") if s.strip()]

    for skill in skills:
        skill_id = store.upsert_node(
            "Skill",
            {"id": skill, "name": skill},
        )
        store.upsert_edge(person_id, "HAS_SKILL", skill_id)

    # ---- Employment ----
    employment = extracted.get("employment_history")
    if employment:
        emp_id = store.upsert_node(
            "Employment",
            {"id": f"{name}_employment", "description": employment},
        )
        store.upsert_edge(person_id, "HAS_EMPLOYMENT", emp_id)

    # ---- Education ----
    education = extracted.get("education_history")
    if education:
        edu_id = store.upsert_node(
            "Education",
            {"id": f"{name}_education", "description": education},
        )
        store.upsert_edge(person_id, "HAS_EDUCATION", edu_id)

    # ---- Projects ----
    projects = extracted.get("projects")
    if projects:
        proj_id = store.upsert_node(
            "Project",
            {"id": f"{name}_project", "description": projects},
        )
        store.upsert_edge(person_id, "WORKED_ON", proj_id)

    # ---- Accomplishments ----
    accomplishments = extracted.get("accomplishments")
    if accomplishments:
        acc_id = store.upsert_node(
            "Accomplishment",
            {"id": f"{name}_accomplishment", "description": accomplishments},
        )
        store.upsert_edge(person_id, "HAS_ACCOMPLISHMENT", acc_id)

    print("Graph successfully built.")