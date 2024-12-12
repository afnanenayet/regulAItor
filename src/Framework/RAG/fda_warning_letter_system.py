# File: Framework/RAG/fda_warning_letter_system.py

import os
import json
from qdrant_client import QdrantClient
from qdrant_client.http.models import PointStruct
from qdrant_client.http.exceptions import UnexpectedResponse
from sentence_transformers import SentenceTransformer
from autogen import AssistantAgent
from autogen.agentchat.contrib.retrieve_user_proxy_agent import RetrieveUserProxyAgent
from dotenv import load_dotenv

class FDAWarningLetterSystem:
    def __init__(self):
        load_dotenv()
        self.qdrant_host = os.getenv("QDRANT_HOST", "localhost")
        self.qdrant_port = int(os.getenv("QDRANT_PORT", "6333"))
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.openai_model = os.getenv("OPENAI_MODEL", "gpt-4")
        self.client = QdrantClient(host=self.qdrant_host, port=self.qdrant_port)
        self.embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
        self.collection_name = "violations_collection"

    def prepare_data(self):
        with open(os.path.join(os.path.dirname(__file__), 'data', 'violations_data.json'), 'r') as f:
            data_samples = json.load(f)

        vectors = []
        for idx, entry in enumerate(data_samples):
            for term_idx, term in enumerate(entry['violated_terms']):
                vector = self.embedding_model.encode(term).tolist()
                payload = {
                    'letter_name': entry['letter_name'],
                    'violated_term': term,
                    'recommendations': entry['recommendations']
                }
                vectors.append(PointStruct(id=idx*100 + term_idx, vector=vector, payload=payload))

        vector_size = len(vectors[0].vector)

        try:
            self.client.get_collection(collection_name=self.collection_name)
            print(f"Collection '{self.collection_name}' exists. Deleting it...")
            self.client.delete_collection(collection_name=self.collection_name)
        except UnexpectedResponse:
            print(f"Collection '{self.collection_name}' does not exist. Creating a new one...")

        self.client.create_collection(
            collection_name=self.collection_name,
            vectors_config={
                "size": vector_size,
                "distance": 'Cosine'
            }
        )

        self.client.upsert(
            collection_name=self.collection_name,
            points=vectors
        )

        print("Data uploaded to Qdrant successfully.")

    def run_agent(self, user_query):
        llm_config = {
            "config_list": [
                {
                    "model": self.openai_model,
                    "api_key": self.openai_api_key,
                    "tags": ["gpt", "tool"]
                }
            ]
        }

        assistant = AssistantAgent(
            name="assistant",
            system_message="You are a compliance assistant. Provide violated terms and corresponding recommendations based on user queries.",
            llm_config=llm_config,
        )

        retrieve_config = {
            "task": "qa",
            "vector_db": "qdrant",
            "collection_name": self.collection_name,
            "docs_path": None,
            "db_config": {"client": self.client},
            "embedding_function": self.embedding_model.encode,
            "model": self.openai_model,
            "get_or_create": False,
            "overwrite": False,
        }

        ragproxyagent = RetrieveUserProxyAgent(
            name="ragproxyagent",
            human_input_mode="NEVER",
            max_consecutive_auto_reply=5,
            retrieve_config=retrieve_config,
            code_execution_config=False,
        )

        def custom_message_generator(sender, recipient, kwargs):
            user_query = kwargs.get('problem')
            if not user_query:
                raise ValueError("User query ('problem') not provided in kwargs.")

            query_embedding = sender._retrieve_config['embedding_function'](user_query).tolist()

            search_results = sender._retrieve_config['db_config']['client'].search(
                collection_name=sender._retrieve_config['collection_name'],
                query_vector=query_embedding,
                limit=2
            )

            context = ''
            if search_results:
                for result in search_results:
                    violated_term = result.payload.get('violated_term', '')
                    recommendations = '\n'.join(result.payload.get('recommendations', []))
                    context += (
                        f"Violated Term: {violated_term}\n"
                        f"Recommendations:\n{recommendations}\n"
                        f"---\n"
                    )
            else:
                context = "No relevant context found."

            print("Context:\n", context)

            message = (
                "You are a compliance assistant. Provide violated terms and corresponding recommendations "
                "based on user queries and the provided context.\n"
                "Be concise and specific.\n\n"
                f"User's question: {user_query}\n\n"
                f"Context:\n{context}\n"
            )
            return message

        chat_results = ragproxyagent.initiate_chat(
            assistant,
            message=custom_message_generator,
            problem=user_query
        )

        assistant_response = ''
        for message in chat_results.chat_history:
            if message['name'] == 'assistant' and message['role'] == 'user':
                assistant_response = message['content']
                break

        if not assistant_response:
            assistant_response = 'No response received.'

        print("\nAssistant's Response:")
        print(assistant_response)

        return assistant_response

    def input_guardrail(self, user_input):
        # Implement your input validation logic here
        # For the sake of example, let's assume all inputs are valid
        return {'should_block': 'No'}

    def summary_generator(self, warning_letter):
        # Implement your summary extraction logic here
        # For now, return a placeholder
        return {'summary': 'This is a summary of the warning letter.'}

    def retrieve_similar_cases(self, summary_embedding):
        # Implement logic to retrieve similar cases based on the embedding
        # For now, return a placeholder
        return ['Similar case 1', 'Similar case 2']

    def get_embedding(self, text):
        return self.embedding_model.encode(text).tolist()
