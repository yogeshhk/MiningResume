import json
from typing import List

from .neo4j_service import Neo4jService
from .llm_service import LLMService


class Neo4jChatbot:
    """
    Chatbot that can query a Neo4j graph and answer questions using an LLM.
    Maintains a short-term memory of previous queries (default 4 contexts).
    """

    def __init__(self, neo4j_service: Neo4jService, llm_service: LLMService, memory_size: int = 4):
        """
        Args:
            neo4j_service: Instance of Neo4jService
            llm_service: Instance of LLMService (e.g., google/flan-t5-large)
            memory_size: Number of previous contexts to retain in memory
        """
        self.neo4j_service = neo4j_service
        self.llm_service = llm_service
        self.memory_size = memory_size
        self.memory: List[str] = []

    def ask(self, query: str) -> str:
        """
        Ask a question to the chatbot. Combines graph context and memory.

        Args:
            query: The user's question

        Returns:
            Answer string from the LLM
        """
        # Add query to memory
        self.memory.append(query)
        if len(self.memory) > self.memory_size:
            self.memory.pop(0)

        # Retrieve graph data
        graph_data = self.neo4j_service.get_full_graph()

        # Flatten nodes and edges into a context string
        context_str = json.dumps(graph_data, indent=2)

        # Construct the prompt for LLM
        prompt = (
            f"You are a knowledgeable assistant. Use the following graph data "
            f"to answer the question.\n\n"
            f"Graph Data:\n{context_str}\n\n"
            f"Previous memory: {json.dumps(self.memory[:-1], indent=2)}\n\n"
            f"Question: {query}\nAnswer:"
        )

        # Use LLM service to get answer
        answer = self.llm_service.ask(prompt)
        return answer
