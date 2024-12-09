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

    retrieve_config = {
        "task": "qa",
        "vector_db": "qdrant",
        "collection_name": "violations_collection",
        "docs_path": None,
        "db_config": {"client": client},
        "embedding_function": embedding_model.encode,
        "model": openai_model,
        "get_or_create": False,
        "overwrite": False,
    }

    ragproxyagent = RetrieveUserProxyAgent(
        name="ragproxyagent",
        human_input_mode="NEVER",
        max_consecutive_auto_reply=2,
        retrieve_config=retrieve_config,
        code_execution_config=False,
    )

    user_query = input("Enter your query: ")

    assistant.reset()

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
            break  # Stop after finding the assistant's response

    if not assistant_response:
        assistant_response = 'No response received.'

    print("\nAssistant's Response:")
    print(assistant_response)

if __name__ == "__main__":
    main()