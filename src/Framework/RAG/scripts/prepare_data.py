# scripts/prepare_data.py

import os
import json
from qdrant_client import QdrantClient
from qdrant_client.http.models import PointStruct
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv

def main():
    load_dotenv()
    with open('../data/violations_data.json', 'r') as f:
        data_samples = json.load(f)
    qdrant_host = os.getenv("QDRANT_HOST", "localhost")
    qdrant_port = int(os.getenv("QDRANT_PORT", "6333"))
    client = QdrantClient(host=qdrant_host, port=qdrant_port)
    embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
    # Prepare data for Qdrant
    vectors = []
    for idx, entry in enumerate(data_samples):
        for term_idx, term in enumerate(entry['violated_terms']):
            vector = embedding_model.encode(term).tolist()
            payload = {
                'letter_name': entry['letter_name'],
                'violated_term': term,
                'recommendations': entry['recommendations']
            }
            vectors.append(PointStruct(id=idx*100 + term_idx, vector=vector, payload=payload))

    # Create a collection and upload data to Qdrant
    vector_size = len(vectors[0].vector)
    client.recreate_collection(
        collection_name="violations_collection",
        vectors_config={
            "size": vector_size,
            "distance": 'Cosine'  # or 'Euclidean' based on your preference
        }
    )

    client.upsert(
        collection_name="violations_collection",
        points=vectors
    )

    print("Data uploaded to Qdrant successfully.")

if __name__ == "__main__":
    main()