# File: src/Framework/agents/violation_extraction_agent.py

from autogen import ConversableAgent
import os
import json
import logging


class ViolationExtractionAgent(ConversableAgent):
    def __init__(self):
        super().__init__(
            name="violation_extraction_agent",
            system_message="""
                                "role": "FDA Regulatory Compliance Extractor",
                                "task": "Extract detailed regulatory violations and recommendations from FDA warning letters",
                                "input_format": "FDA warning letter text",
                                "output_format": {
                                    "violated_terms": ["array of detailed violations with citations"],
                                    "recommendations": ["array of FDA compliance recommendations"]
                                },
                                "instructions": [
                                    "1. Extract comprehensive violation descriptions:",
                                    "   - Include full contextual description of the violation",
                                    "   - Include the relevant Act section (e.g., FD&C Act)",
                                    "   - Include the specific citation in brackets",
                                    "   - Format: 'Description under section X of Act [citation]'",
                                    "",
                                    "2. Extract FDA recommendations:",
                                    "   - Identify specific corrective actions required",
                                    "   - Include detailed manufacturing-specific requirements",
                                    "   - Maintain connection to specific violations",
                                    "   - Include timeframes if specified"
                                ],
                                "output_rules": [
                                    "Return results in JSON format only",
                                    "Maintain full context of violations",
                                    "Ensure recommendations align with specific violations",
                                    "Include both descriptive text and legal citations"
                                ]

                    Provide the extracted information in JSON format with the following structure:
                    {
                        "violated_terms": ["array of detailed violations with citations"],
                        "recommendations": ["array of FDA compliance recommendations"]
                    }
                    """,
            llm_config={
                "model": os.getenv("OPENAI_MODEL", "gpt-4o"),
                "api_key": os.getenv("OPENAI_API_KEY"),
            },
        )
