# File: src/Framework/agents/conversation_workflow.py

def conversation_workflow(agent_manager):
    warning_letter = agent_manager.context.get("warning_letter")

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
    for term in violated_terms:
        similar_result = agent_manager.send_and_receive(
            sender="similarity_search_agent",
            recipient="coordinator_agent",
            message={"violated_term": term}
        )
        similar_cases.append({
            "violated_term": term,
            "similar_cases": similar_result.get("similar_cases", [])
        })

    # Regulation Content Agent
    regulation_texts = agent_manager.send_and_receive(
        sender="regulation_content_agent",
        recipient="coordinator_agent",
        message={"violated_terms": violated_terms}
    )

    # Recommendation Agent
    recommendations = agent_manager.send_and_receive(
        sender="recommendation_agent",
        recipient="coordinator_agent",
        message={
            "violations": final_extraction,
            "regulation_texts": regulation_texts.get("regulation_texts", {}),
            "similar_cases": similar_cases
        }
    )

    # Compile the final response
    return {
        "violated_terms": final_extraction.get("violated_terms", []),
        "recommendations": final_extraction.get("recommendations", []),
        "similar_cases": similar_cases,
        "regulation_texts": regulation_texts.get("regulation_texts", {}),
        "final_recommendations": recommendations.get("recommendations", [])
    }