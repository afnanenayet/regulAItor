import json
import os
from pathlib import Path

from dotenv import load_dotenv
from qdrant_client import QdrantClient
from qdrant_client.http.exceptions import UnexpectedResponse
from qdrant_client.http.models import PointStruct
from sentence_transformers import SentenceTransformer


def main():
    _ = load_dotenv()
    with open(
        Path(__file__).parent.parent.parent.parent
        / "data/output/validated_summaries.json",
        "r",
    ) as f:
        data_samples = json.load(f)

    qdrant_host = os.getenv("QDRANT_HOST", "localhost")
    qdrant_port = int(os.getenv("QDRANT_PORT", "6333"))
    client = QdrantClient(host=qdrant_host, port=qdrant_port)

    embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

    vectors = []
    for idx, entry in enumerate(data_samples):
        for term_idx, term in enumerate(entry["violated_terms"]):
            vector = embedding_model.encode(term).tolist()
            payload = {
                "letter_name": entry["letter_name"],
                "violated_term": term,
                "recommendations": entry["recommendations"],
            }
            vectors.append(
                PointStruct(id=idx * 100 + term_idx, vector=vector, payload=payload)
            )

    collection_name = "violations_collection"
    vector_size = len(vectors[0].vector)

    try:
        client.get_collection(collection_name=collection_name)
        print(f"Collection '{collection_name}' exists. Deleting it...")
        client.delete_collection(collection_name=collection_name)
    except UnexpectedResponse:
        print(f"Collection '{collection_name}' does not exist. Creating a new one...")

    client.create_collection(
        collection_name=collection_name,
        vectors_config={
            "size": vector_size,
            "distance": "Cosine",  # or 'Euclidean' based on your preference
        },
    )

    client.upsert(collection_name=collection_name, points=vectors)

    print("Data uploaded to Qdrant successfully.")


if __name__ == "__main__":
    main()
