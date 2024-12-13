# File: /Framework/agents/conversation_workflow.py
import re


def conversation_workflow(agent_manager):
    warning_letter = agent_manager.context.get("warning_letter")
    template = agent_manager.context.get("template", "")
    
    # Input Validation Agent
    validation_result = agent_manager.send_and_receive(
        sender="input_validation_agent",
        recipient="coordinator_agent",
        message={"warning_letter": warning_letter}
    )
    if not validation_result.get("is_valid", False):
        return {"error": "Invalid warning letter"}
    
    # Violation Extraction Agent
    extraction_result = agent_manager.send_and_receive(
        sender="violation_extraction_agent",
        recipient="coordinator_agent",
        message={"warning_letter": warning_letter}
    )
    
    # Validation Agent
    validation_feedback = agent_manager.send_and_receive(
        sender="validation_agent",
        recipient="coordinator_agent",
        message={
            "extraction_result": extraction_result,
            "warning_letter": warning_letter
        }
    )
    
    # Check if validation is approved
    status = validation_feedback.get("status")
    if status == "APPROVED":
        final_extraction = extraction_result
    elif status == "REJECTED":
        # Use the revised summary from the validation feedback
        final_extraction = validation_feedback.get("revised_summary", {})
    else:
        return {"error": "Validation failed"}
    
    # Similarity Search Agent
    similar_cases = []
    violated_terms = final_extraction.get("violated_terms", [])

    violated_term_numbers = []
    for term in violated_terms:
        matches = re.findall(r'\b\d+\sCFR\s\d+(?:\.\d+)?', term)
        violated_term_numbers.extend(matches)
        
        similar_result = agent_manager.send_and_receive(
            sender="similarity_search_agent",
            recipient="coordinator_agent",
            message={"violated_term": term}
        )
        similar_cases.append({
            "violated_term": term,
            "similar_cases": similar_result.get("similar_cases", [])
        })

    violated_term_numbers = list(set(violated_term_numbers)) #Remove duplicates
    # Regulation Content Agent
    regulation_texts_result = agent_manager.send_and_receive(
        sender="regulation_content_agent",
        recipient="coordinator_agent",
        message={"regulations": violated_term_numbers}
    )
    regulation_texts = regulation_texts_result.get("regulation_texts", {})
    
    # Recommendation Agent
    recommendations_result = agent_manager.send_and_receive(
        sender="recommendation_agent",
        recipient="coordinator_agent",
        message={
            "violations": final_extraction,
            "regulation_texts": regulation_texts,
            "similar_cases": similar_cases
        }
    )
    final_recommendations = recommendations_result.get("recommendations", [])
    
    # Corrective Action Agent
    corrective_action_result = agent_manager.send_and_receive(
        sender="corrective_action_agent",
        recipient="coordinator_agent",
        message={
            "violated_terms": violated_terms,
            "recommendations": final_recommendations,
            "regulation_texts": regulation_texts,
            "template": template
        }
    )
    corrective_action_plan = corrective_action_result.get("corrective_action_plan", "")
    
    # Corrective Action Validation Agent
    corrective_action_validation = agent_manager.send_and_receive(
        sender="corrective_action_validation_agent",
        recipient="coordinator_agent",
        message={
            "corrective_action_plan": corrective_action_plan,
            "violated_terms": violated_terms,
            "template": template
        }
    )
    
    # Check validation feedback
    status = corrective_action_validation.get("status")
    if status == "APPROVED":
        final_corrective_action_plan = corrective_action_plan
    elif status == "CHANGES_REQUIRED":
        final_corrective_action_plan = None  # You may implement a revision loop here
    else:
        return {"error": "Corrective action validation failed"}
    
    # Compile the final response
    result = {
        "violated_terms": violated_terms,
        "recommendations": final_recommendations,
        "similar_cases": similar_cases,
        "regulation_texts": regulation_texts,
        "corrective_action_plan": final_corrective_action_plan,
        "validation_feedback": corrective_action_validation
    }
    
    return result