# File: Framework/agents/recommendation_agent.py

from autogen import AssistantAgent
import os
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
from qdrant_client.http.models import Filter
from dotenv import load_dotenv

class RecommendationAgent(AssistantAgent):
    def __init__(self):
        load_dotenv()
        super().__init__(
            name="recommendation_agent",
            system_message="You generate recommendations based on extracted violations and regulations.",
            llm_config={
                "model": os.getenv("OPENAI_MODEL", "gpt-4"),
                "api_key": os.getenv("OPENAI_API_KEY"),
            },
        )
        # Initialize the RAG components
        qdrant_host = os.getenv("QDRANT_HOST", "localhost")
        qdrant_port = int(os.getenv("QDRANT_PORT", "6333"))
        self.client = QdrantClient(host=qdrant_host, port=qdrant_port)
        self.embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
        self.collection_name = "violations_collection"

    def handle_message(self, message):
        violations = message.get("violations", [])
        # Retrieve recommendations using RAG
        rag_recommendations = self.retrieve_recommendations(violations)
        # Combine RAG recommendations with regulation texts if needed
        recommendations = self.generate_recommendations(violations, rag_recommendations)
        return {"recommendations": recommendations}

    def retrieve_recommendations(self, violations):
        # Generate embeddings for violations
        violation_embeddings = [self.embedding_model.encode(v) for v in violations]
        recommendations = []
        for vec in violation_embeddings:
            search_results = self.client.search(
                collection_name=self.collection_name,
                query_vector=vec,
                limit=2  # Adjust as needed
            )
            for result in search_results:
                recs = result.payload.get('recommendations', [])
                recommendations.extend(recs)
        return recommendations

    def generate_recommendations(self, violations, rag_recommendations):
        # Use the LLM to generate recommendations, incorporating RAG results
        prompt = f"""
You are a compliance assistant helping to generate recommendations based on past FDA warning letters.

Violations:
{violations}

Previous Recommendations:
{rag_recommendations}

Based on the violations and previous recommendations, provide updated recommendations to address each violation.
"""
        response = self.llm.generate(prompt)
        recommendations = response.strip()
        return recommendations