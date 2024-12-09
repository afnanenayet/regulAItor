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

    qdrant_host = os.getenv("QDRANT_HOST", "localhost")
    qdrant_port = int(os.getenv("QDRANT_PORT", "6333"))
    openai_api_key = os.getenv("OPENAI_API_KEY")
    openai_model = os.getenv("OPENAI_MODEL", "gpt-4")

    client = QdrantClient(host=qdrant_host, port=qdrant_port)

    embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

    llm_config = {
        "config_list": [
            {
                "model": openai_model,
                "api_key": openai_api_key,
                "tags": ["gpt", "tool"]
            }
        ]
    }

    assistant = AssistantAgent(
        name="assistant",
        system_message="You are a compliance assistant. Provide violated terms and corresponding recommendations based on user queries.",
        llm_config=llm_config,
    )

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

    user_query = input("Enter your query: ")

    assistant.reset()

    chat_results = ragproxyagent.initiate_chat(
        assistant,
        message=ragproxyagent.message_generator,
        problem=user_query
    )

    print("\nAssistant's Response:")
    for message in chat_results:
        print(f"{message.sender}: {message.content}")

if __name__ == "__main__":
    main()