
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List

@dataclass
class WarningLetter:
    letter_id: str
    letter_name: str
    content: str
    violated_terms: List[str]
    recommendations: List[str]
    processed_date: datetime = field(default_factory=datetime.now)
    metadata: Dict = field(default_factory=dict)

    def __post_init__(self):
        if not self.letter_id:
            raise ValueError("letter_id cannot be empty")
        if not self.letter_name:
            raise ValueError("letter_name cannot be empty")
        if not isinstance(self.violated_terms, list):
            raise TypeError("violated_terms must be a list")
        if not isinstance(self.recommendations, list):
            raise TypeError("recommendations must be a list")

    def to_dict(self) -> Dict:
        return {
            "letter_id": self.letter_id,
            "letter_name": self.letter_name,
            "violated_terms": self.violated_terms,
            "recommendations": self.recommendations,
            "processed_date": self.processed_date.isoformat(),
            "metadata": self.metadata
        }

