from dataclasses import dataclass
from qdrant_client.models import Distance

@dataclass
class QdrantConfig:
    url: str = "http://localhost:6333"
    collection_name: str = "fda_warnings"
    vector_size: int = 768
    distance: Distance = Distance.COSINE