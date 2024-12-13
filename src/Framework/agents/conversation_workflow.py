# agents/conversation_workflow.py

from autogen import GroupChatManager
import logging

async def conversation_workflow(group_chat):
    # Access context if needed
    warning_letter = group_chat.context.get("warning_letter")
    template = group_chat.context.get("template", "")
    logging.debug(f"Received warning letter: {warning_letter[:100]}...")  # Log first 100 characters
    logging.debug(f"Received template: {template[:100]}...")  # Log first 100 characters
    # Create a GroupChatManager instance
    
    for agent in group_chat.agents:
        agent.context = group_chat.context
    
    
    group_chat_manager = GroupChatManager(group_chat)
    initiating_agent = group_chat.agents[0]
    
    # Agent initiates the chat with an initial message
    initiating_message = f"Please review the following FDA warning letter and prepare corrective actions:\n\n{warning_letter}"

    initiating_agent.initiate_chat(
        group_chat_manager, message=initiating_message
    )
    
    # Start the chat asynchronously
    await group_chat_manager.a_run_chat()

        # After the chat
    logging.debug("Conversation workflow completed.")
    logging.debug(f"Group chat messages: {group_chat.messages}")
    
    for msg in group_chat.messages:
        logging.debug(f"{msg['role']} ({msg.get('name', 'N/A')}): {msg['content']}")
    # After the chat, extract results from agent contexts
    result = {}
    for agent in group_chat.agents:
        if agent.name == "corrective_action_agent":
            corrective_action_plan = agent.context.get("corrective_action_plan", "")
            result["corrective_action_plan"] = corrective_action_plan
        # Extract other necessary data from agents as needed
    return result