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
from .similar_case_agent import Similar_case_Recommendation
from .Initiating_agent import InitiatingAgent
import json


import logging

initiating_agent = InitiatingAgent()
input_validation_agent = InputValidationAgent()
violation_extraction_agent = ViolationExtractionAgent()
validation_agent = ValidationAgent()
similarity_search_agent = SimilaritySearchAgent()
regulation_content_agent = RegulationContentAgent()
recommendation_agent = RecommendationAgent()
similar_agent = Similar_case_Recommendation()
corrective_action_agent = CorrectiveActionAgent()
corrective_action_validation_agent = CorrectiveActionValidationAgent()


agents = [
    initiating_agent,
    input_validation_agent,
    violation_extraction_agent,
    validation_agent,
    similarity_search_agent,
    regulation_content_agent,
    recommendation_agent,
    similar_agent,
    corrective_action_agent,
    corrective_action_validation_agent,
]


def state_transition(last_speaker, groupchat):
    context = groupchat.context
    messages = groupchat.messages

    if len(messages) <= 1:
        return initiating_agent
    if last_speaker is initiating_agent:
        return input_validation_agent
    elif last_speaker is input_validation_agent:
        # Check if input validation passed
        response = input_validation_agent.handle_message()
        print(f"Input validation response: {response}")
        validation_result = context.get("input_validation_result")  # True or False
        valid_template = context.get("Valid_Template")
        logging.debug(f"Input validation result: {validation_result}")
        print(f"Input validation result: {validation_result}")
        print(f"Template validation result: {valid_template}")
        if validation_result and valid_template:
            # Proceed to violation_extraction_agent
            return violation_extraction_agent
        else:
            context["user_input_required"] = True
            return None

    elif last_speaker is violation_extraction_agent:
        return validation_agent

    elif last_speaker is validation_agent:
        try:
            last_validation = validation_agent.last_message()

            # Extract the JSON string from the dict's content field
            last_validation = last_validation["content"].replace("```json", "").replace("```", "").strip()

            json_data = json.loads(last_validation)
            if json_data.get("status") == "APPROVED":
                context["summary"] = {
                    "violated_terms": json_data["summary"]["violated_terms"],
                    "recommendations": json_data["summary"]["recommendations"],
                }
                return similarity_search_agent
            elif json_data.get("status") == "REJECTED":
                context["summary"] = {
                    "violated_terms": json_data["revised_summary"][
                        "violated_terms"
                    ],
                    "recommendations": json_data["revised_summary"][
                        "recommendations"
                    ],
                }
                return violation_extraction_agent

        except (json.JSONDecodeError, TypeError) as e:
            print(f"Error exception: {str(e)}")
            print(f"Debug - Failed validation content: {last_validation}")
            return violation_extraction_agent


    elif last_speaker is similarity_search_agent:
        # Proceed to regulation_content_agent
        return similar_agent

    elif last_speaker is similar_agent:
        context["similar_case"] = similar_agent.last_message()
        return regulation_content_agent

    elif last_speaker is regulation_content_agent:
        # Proceed to recommendation_agent
        print(f"HERE IS regu11: {context.get('regulation_full_texts')}")
        return recommendation_agent

    elif last_speaker is recommendation_agent:
        # Proceed to corrective_action_agent
        print(context["recommendations"])
        return corrective_action_agent

    elif last_speaker is corrective_action_agent:
        print(context.get("corrective_action_plan"))
        # Proceed to corrective_action_validation_agent
        return corrective_action_validation_agent

    elif last_speaker is corrective_action_validation_agent:
        last_validation = corrective_action_validation_agent.last_message()

        if isinstance(last_validation, dict) and "content" in last_validation:
            last_validation = last_validation["content"]

        last_validation = (
            last_validation.replace("```json", "").replace("```", "").strip()
        )

        json_data = json.loads(last_validation)
        is_valid = True
        if json_data.get("status") == "APPROVED":
            print(
                f"HERE IS the Approved Corrective Action: {context.get('corrective_action_plan')}"
            )
            context["Approved_corrective_action_plan"] = context.get(
                "corrective_action_plan"
            )
        elif json_data.get("status") == "REJECTED":
            feedback = json_data.get("feedback")
            context["revision_feedback"] = feedback
            return corrective_action_agent

    else:
        # Default to terminating the workflow
        return None


group_chat = GroupChat(
    agents=agents,
    messages=[],
    max_round=30,
    speaker_selection_method=state_transition,
    allow_repeat_speaker=True,
)
