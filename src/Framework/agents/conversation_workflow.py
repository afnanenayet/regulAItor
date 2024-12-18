from autogen import GroupChatManager
import logging
from .agent_manager import initiating_agent


async def conversation_workflow(group_chat):
    warning_letter = group_chat.context.get("warning_letter")
    template = group_chat.context.get("template", "")

    for agent in group_chat.agents:
        agent.context = group_chat.context

    group_chat_manager = GroupChatManager(group_chat)

    if not warning_letter:
        return {"error": "Warning letter is missing or empty"}
    initiating_message = f"Warning letter received:\n\n{warning_letter}"
    initiating_agent.initiate_chat(group_chat_manager, message=initiating_message)

    if group_chat.context.get("user_input_required"):
        return {
            False: (
                f"User's input is not valid because of "
                f"warning letter: {group_chat.context.get('input_validation_result_feedback', '')} "
                f"OR template: {group_chat.context.get('valid_Template_feedback', '')}"
            )
        }

    # Extract results from agent context
    for agent in group_chat.agents:
        if agent.name == "corrective_action_agent":
            corrective_action_plan = agent.context.get("corrective_action_plan", "")

    return {True: corrective_action_plan}
