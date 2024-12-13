# File: /Framework/agents/agent_manager.py

import os
from autogen import GroupChat

from .input_validation_agent import InputValidationAgent
from .violation_extraction_agent import ViolationExtractionAgent
from .validation_agent import ValidationAgent
from .similarity_search_agent import SimilaritySearchAgent
from .regulation_content_agent import RegulationContentAgent
from .recommendation_agent import RecommendationAgent
from .corrective_action_agent import CorrectiveActionAgent
from .corrective_action_validation_agent import CorrectiveActionValidationAgent

input_validation_agent = InputValidationAgent()
violation_extraction_agent = ViolationExtractionAgent()
validation_agent = ValidationAgent()
similarity_search_agent = SimilaritySearchAgent()
regulation_content_agent = RegulationContentAgent()
recommendation_agent = RecommendationAgent()
corrective_action_agent = CorrectiveActionAgent()
corrective_action_validation_agent = CorrectiveActionValidationAgent()



agents = [
    input_validation_agent,
    violation_extraction_agent,
    validation_agent,
    similarity_search_agent,
    regulation_content_agent,
    recommendation_agent,
    corrective_action_agent,
    corrective_action_validation_agent,
]

group_chat = GroupChat(
    agents=agents,
    messages=[],
    max_round=10,
    speaker_selection_method="round_robin",  # You can choose other methods like "auto"
    allow_repeat_speaker=True,
)
