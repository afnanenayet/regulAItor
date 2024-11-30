from pathlib import Path

from pydantic import BaseModel
from qdrant_client.models import Distance


class QdrantConfig(BaseModel):
    """Config options for the qdrant vector database."""

    url: str = "http://localhost:6333"
    """Connection URL to your cloud or local qdrant instance."""

    collection_name: str = "fda_warnings"
    """The name of the collection to spin up."""

    vector_size: int = 768
    # TODO: add validator to guarantee positive int
    distance: Distance = Distance.COSINE


class AppConfig(BaseModel):
    """
    An easy configuration class for running the framework on the backend. This provides a unified
    interface so that developers can spin up the backend, input keys, etc.

    Default values will automatically be applied if not provided by the user.
    """

    qdrant_config: QdrantConfig
    autogen_config: Path
    """
    Path to your autogen config file.

    This should be a JSON file with your OpenAI credentials, in the form defined by
    the `OAI_CONFIG_LIST` in this repo.
    """
