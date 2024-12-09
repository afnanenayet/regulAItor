# scripts/run_agent.py

import os
from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer
import autogen
from autogen import AssistantAgent
from autogen.agentchat.contrib.retrieve_user_proxy_agent import RetrieveUserProxyAgent
from dotenv import load_dotenv

def main():
    load_dotenv()

    # Get environment variables
    qdrant_host = os.getenv("QDRANT_HOST", "localhost")
    qdrant_port = int(os.getenv("QDRANT_PORT", "6333"))
    openai_api_key = os.getenv("OPENAI_API_KEY")
    openai_model = os.getenv("OPENAI_MODEL", "gpt-4")

    # Initialize Qdrant client
    client = QdrantClient(host=qdrant_host, port=qdrant_port)

    # Initialize the embedding model
    embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

    # Define LLM configuration
    llm_config = {
        "config_list": [
            {
                "model": openai_model,
                "api_key": openai_api_key,
                "tags": ["gpt", "tool"]
            }
        ]
    }

    # Initialize the AssistantAgent
    assistant = AssistantAgent(
        name="assistant",
        system_message="You are a compliance assistant. Provide violated terms and corresponding recommendations based on user queries.",
        llm_config=llm_config,
    )

    # Initialize the RetrieveUserProxyAgent
    ragproxyagent = RetrieveUserProxyAgent(
        name="ragproxyagent",
        human_input_mode="NEVER",
        max_consecutive_auto_reply=3,
        retrieve_config={
            "task": "violations_lookup",
            "vector_db": "qdrant",
            "collection_name": "violations_collection",
            "db_config": {"client": client},
            "embedding_function": embedding_model.encode,
            "model": openai_model,
        },
        code_execution_config=False,
    )

    # Example user query
    user_query = input("Enter your query: ")

    # Reset the assistant for a new conversation
    assistant.reset()

    # Initiate the chat
    chat_results = ragproxyagent.initiate_chat(
        assistant,
        message=ragproxyagent.message_generator,
        problem=user_query
    )

    # Print the assistant's response
    print("\nAssistant's Response:")
    for message in chat_results:
        print(f"{message.sender}: {message.content}")

if __name__ == "__main__":
    main()