import sys
from pathlib import Path

project_root = Path(__file__).resolve().parent.parent
sys.path.append(str(project_root))

import json
import streamlit as st
from pathlib import Path

from src.llm_based.services.neo4j_chatbot import Neo4jChatbot
from src.llm_based.config.settings import settings
from src.llm_based.services.llm_service import LLMService
from src.llm_based.services import create_cache_service, Neo4jService
from src.llm_based.adapters import HuggingFaceAdapter

st.set_page_config(page_title="Resume Graph & Chatbot", layout="wide")
st.title("Resume Graph & Chatbot")

# Setup LLM Service
cache_service = create_cache_service()
llm_provider = HuggingFaceAdapter()
llm_service = LLMService(provider=llm_provider, cache_service=cache_service)

# Setup Neo4j
neo4j_service = Neo4jService()
chatbot = Neo4jChatbot(neo4j_service, llm_service)


# Upload resumes
# Currently, this upload functionality uploads the resume to the /data folder
# We would need to run the main.py again to get the resume parsed and stored in json format
st.sidebar.header("Upload Resumes (PDF)")
uploaded_files = st.sidebar.file_uploader(
    "Select PDF resumes", type="pdf", accept_multiple_files=True
)

if uploaded_files:
    st.sidebar.success(f"{len(uploaded_files)} file(s) uploaded.")

    for uploaded_file in uploaded_files:
        # Save temporarily
        temp_path = Path("data") / uploaded_file.name
        temp_path.parent.mkdir(exist_ok=True)
        with open(temp_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        # Parse JSON already generated
        st.sidebar.text(f"Adding {uploaded_file.name} to Neo4j graph...")
        json_path = Path("parsed_resume_llm_based.json")
        if json_path.exists():
            with open(json_path, "r", encoding="utf-8") as f:
                resume_data = json.load(f)
            neo4j_service.upsert_resume_graph(resume_data, overwrite=False)
        else:
            st.warning(f"JSON not found for {uploaded_file.name}, skipping graph update.")

# Show graph
st.header("Neo4j Resume Graph")
graph_data = neo4j_service.get_full_graph()

if graph_data["nodes"]:
    import pyvis.network as net

    net_graph = net.Network(height="600px", width="100%", notebook=False)
    for node in graph_data["nodes"]:
        net_graph.add_node(
            node["id"], label=node["label"], title=json.dumps(node["properties"], indent=2)
        )
    for edge in graph_data["edges"]:
        net_graph.add_edge(edge["from"], edge["to"], label=edge["type"])
    
    net_graph.show_buttons(filter_=["physics"])
    net_graph.save_graph("graph.html")
    st.components.v1.html(open("graph.html", "r").read(), height=600)
else:
    st.info("No graph data found. Upload resumes to populate graph.")

# Chatbot Query
st.header("Ask Questions about Resumes")
user_question = st.text_input("Enter your question here:")

if user_question:
    with st.spinner("Thinking..."):
        answer = chatbot.ask(user_question)
    st.markdown(f"**Answer:** {answer}")
