# File: src/Framework/agents/agent_manager.py

from autogen import AgentManager

from agents.input_validation_agent import InputValidationAgent
from agents.violation_extraction_agent import ViolationExtractionAgent
from agents.validation_agent import ValidationAgent
from agents.similarity_search_agent import SimilaritySearchAgent
from agents.regulation_content_agent import RegulationContentAgent
from agents.recommendation_agent import RecommendationAgent

# Initialize agents
input_validation_agent = InputValidationAgent()
violation_extraction_agent = ViolationExtractionAgent()
validation_agent = ValidationAgent()
similarity_search_agent = SimilaritySearchAgent()
regulation_content_agent = RegulationContentAgent()
recommendation_agent = RecommendationAgent()

# Create an agent manager
agent_manager = AgentManager(
    [
        input_validation_agent,
        violation_extraction_agent,
        validation_agent,
        similarity_search_agent,
        regulation_content_agent,
        recommendation_agent,
    ],
    llm_config={
        "model": os.getenv("OPENAI_MODEL", "gpt-4"),
        "api_key": os.getenv("OPENAI_API_KEY"),
    },
)