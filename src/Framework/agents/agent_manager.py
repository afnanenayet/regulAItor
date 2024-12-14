# File: /Framework/agents/agent_manager.py

import os
from autogen import GroupChat
import autogen
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

initiating_agent = autogen.UserProxyAgent(
                                            name="Init",
    )

agents = [
    initiating_agent,
    input_validation_agent,
    violation_extraction_agent,
    validation_agent,
    similarity_search_agent,
    regulation_content_agent,
    recommendation_agent,
    corrective_action_agent,
    corrective_action_validation_agent,
]


def state_transition(last_speaker, groupchat):
    context = groupchat.context
    messages = groupchat.messages

    if len(messages) <= 1:
        # Start the conversation with the initiating agent
        return initiating_agent

    if last_speaker is initiating_agent:
        # After initiating, proceed to input validation
        return input_validation_agent

    elif last_speaker is input_validation_agent:
        # Check if input validation passed
        validation_result = context.get("input_validation_result")  # True or False
        if validation_result:
            # Proceed to violation_extraction_agent
            return violation_extraction_agent
        else:
            context['user_input_required'] = True
            return None

    elif last_speaker is violation_extraction_agent:
        # Proceed to validation_agent
        return validation_agent

    elif last_speaker is validation_agent:
        # Check if validation passed
        validation_feedback = context.get("validation_feedback", {})
        if validation_feedback.get("status") == "APPROVED":
            # Proceed to similarity_search_agent
            return similarity_search_agent
        else:
            # Re-ask violation_extraction_agent to regenerate
            return violation_extraction_agent

    elif last_speaker is similarity_search_agent:
        # Proceed to regulation_content_agent
        return regulation_content_agent

    elif last_speaker is regulation_content_agent:
        # Proceed to recommendation_agent
        return recommendation_agent

    elif last_speaker is recommendation_agent:
        # Proceed to corrective_action_agent
        return corrective_action_agent

    elif last_speaker is corrective_action_agent:
        # Proceed to corrective_action_validation_agent
        return corrective_action_validation_agent

    elif last_speaker is corrective_action_validation_agent:
        # Check if corrective action plan is approved
        validation_result = context.get("corrective_action_validation", {})
        if validation_result.get("status") == "APPROVED":
            # Finish the workflow
            return None
        else:
            # Re-ask corrective_action_agent to regenerate
            return corrective_action_agent

    else:
        # Default to terminating the workflow
        return None


group_chat = GroupChat(
    agents=agents,  
    messages=[],
    max_round=20,
    speaker_selection_method=state_transition,
    allow_repeat_speaker=True,
)