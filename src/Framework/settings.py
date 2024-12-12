# File: Framework/settings.py

from dataclasses import dataclass

@dataclass
class Settings:
    OPENAI_API_KEY: str = "YOUR_OPENAI_API_KEY"
    QDRANT_HOST: str = "localhost"
    QDRANT_PORT: int = 6333