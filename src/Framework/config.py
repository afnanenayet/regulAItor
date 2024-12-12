# File: Framework/config.py

from dataclasses import dataclass
from qdrant_client.models import Distance

@dataclass
class QdrantConfig:
    host: str = "localhost"
    port: int = 6333
    collection_name: str = "violations_collection"
    vector_size: int = 384  # Adjust based on the embedding model used
    distance: Distance = Distance.COSINE