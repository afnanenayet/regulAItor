# File: src/Framework/agents/validation_agent.py

from autogen import ConversableAgent
import os
import json
import logging

class ValidationAgent(ConversableAgent):
    def __init__(self):
        super().__init__(
            name="validation_agent",
            system_message="""
            {
                "role": "FDA Compliance Validation Agent",
                "task": "Validate extracted violations and recommendations against original warning letter by returning an approval status and summary or revised summary in a json format",
                "validation_criteria": {
                    "1. Violation Context Validation": [
                        "Verify complete violation descriptions are captured",
                        "Confirm both context and citations are accurate",
                        "Check for proper reference to relevant Acts/sections",
                        "Ensure violation descriptions match the original letter"
                    ],
                    "2. Recommendation Validation": [
                        "Verify recommendations address specific manufacturing contexts",
                        "Ensure recommendations match violation contexts",
                        "Confirm technical accuracy of corrective actions",
                        "Check for manufacturing-specific details"
                    ],
                    "3. Completeness Validation": [
                        "Verify all contextual information is preserved",
                        "Confirm no critical details are omitted",
                        "Check for proper connection between violations and recommendations"
                    ]
                },
                "output_format": {
                    "if_approved": {
                        "status": "APPROVED",
                        "summary": {
                            "violated_terms": ["full violation descriptions with citations"],
                            "recommendations": ["detailed corrective actions"]
                    },
                    "if_rejected": {
                        "status": "REJECTED",
                        "feedback": "Detailed explanation of missing context or inaccuracies",
                        "revised_summary": {
                            "violated_terms": ["full violation descriptions with citations"],
                            "recommendations": ["detailed corrective actions"]
                        }
                    }
                }
            }
            """,
            llm_config={
                "model": os.getenv("OPENAI_MODEL", "gpt-4"),
                "api_key": os.getenv("OPENAI_API_KEY"),
            },
        )