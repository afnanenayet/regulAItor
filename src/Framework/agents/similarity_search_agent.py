# File: /Framework/agents/similarity_search_agent.py

from autogen import ConversableAgent
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
import os
import logging

class SimilaritySearchAgent(ConversableAgent):
    def __init__(self):
        super().__init__(
            name="similarity_search_agent",
            system_message="You retrieve similar past violations based on provided violated terms.",
            llm_config={
                "model": os.getenv("OPENAI_MODEL", "gpt-4"),
                "api_key": os.getenv("OPENAI_API_KEY"),
            },
        )
        self.embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
        qdrant_host = os.getenv("QDRANT_HOST", "localhost")
        qdrant_port = int(os.getenv("QDRANT_PORT", "6333"))
        self.clientQ = QdrantClient(host=qdrant_host, port=qdrant_port)
        self.collection_name = "violations_collection"
        
        # Register the retrieval function with a specific trigger
        self.register_reply(
            trigger="retrieve_similar", # Add a specific trigger string
            reply_func=self._retrieve_similar_cases_reply,
            position=0
        )

    def _retrieve_similar_cases_reply(self, recipient, messages, sender, config):
        # Access the violated terms from the nested context structure
        summary = self.context.get('summary', {})
        violated_terms = summary.get('violated_terms', [])
        
        similar_cases = self.retrieve_similar_cases(violated_terms)
        print(f"Similar cases: {similar_cases}")
        self.context["similar_cases"] = similar_cases
        return True, {"role": "assistant", "content": "Similar cases retrieved and stored in context."}


    def retrieve_similar_cases(self, violated_terms):
        similar_cases = []
        for term in violated_terms:
            vector = self.embedding_model.encode(term).tolist()
            search_results = self.clientQ.search(
                collection_name=self.collection_name,
                query_vector=vector,
                limit=5
            )
            for result in search_results:
                payload = result.payload
                similar_cases.append({
                    "letter_name": payload.get('letter_name', ''),
                    "violated_term": payload.get('violated_term', ''),
                    "recommendations": payload.get('recommendations', [])
                })
        return similar_cases