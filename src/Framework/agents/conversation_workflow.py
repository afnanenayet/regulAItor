# agents/conversation_workflow.py

from autogen import GroupChatManager
import logging
from .agent_manager import initiating_agent 

async def conversation_workflow(group_chat):
    warning_letter = group_chat.context.get("warning_letter")
    template = group_chat.context.get("template", "")
    
    for agent in group_chat.agents:
        agent.context = group_chat.context
    
    group_chat_manager = GroupChatManager(group_chat)

    
    # Add error handling for empty warning letter
    if not warning_letter:
        return {"error": "Warning letter is missing or empty"}
        
    # Ensure initial message is set
    initiating_message = f"Warning letter received:\n\n{warning_letter}"
    
    initiating_agent.initiate_chat(
                  group_chat_manager, message=initiating_message
             )
    #print(f"Messages after initiation: {group_chat.messages}")

    # Add error handling for the chat execution
    #await group_chat_manager.a_run_chat()
    
    if group_chat.context.get('user_input_required'):
        return {"user_input_required": True}
        
    # Extract results from agent contexts
    result = {}
    for agent in group_chat.agents:
        if agent.name == "corrective_action_agent":
            corrective_action_plan = agent.context.get("corrective_action_plan", "")
            result["corrective_action_plan"] = corrective_action_plan
            
    return result
