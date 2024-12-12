from autogen import ConversableAgent
import json
import asyncio
from typing import Dict, Optional
import logging
import re
from config import ProcessorConfig, AgentConfig
from rate_limiter import RateLimiter


class FDALetterProcessor:
    def __init__(self, config: ProcessorConfig):
        self.config = config
        self.agent_config = AgentConfig()
        self.rate_limiter = RateLimiter(config.rate_limit_per_minute)
        self.setup_logging()

        # Initialize the agents with updated prompts
        self.summarizer_agent = ConversableAgent(
            name="Extractor",
            system_message="""
            {
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
            }
            """,
            llm_config=self.agent_config.llm_config,
            human_input_mode="NEVER",
        )
        self.validator_agent = ConversableAgent(
            name="Validator",
            system_message="""
                {
                    "role": "FDA Compliance Validation Agent",
                    "task": "Validate extracted violations and recommendations against original warning letter",
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
                            "feedback": "Validation notes on context and completeness"
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
            llm_config=self.agent_config.llm_config,
            human_input_mode="NEVER",
        )

    def setup_logging(self):
        logging.basicConfig(
            level=self.config.log_level,
            format="%(asctime)s - %(levelname)s - %(message)s",
            handlers=[
                logging.FileHandler("fda_processor.log"),
                logging.StreamHandler(),
            ],
        )
        self.logger = logging.getLogger(__name__)

    def process_letter(self, letter_name: str, content: str) -> Optional[Dict]:
        """
        Processes the FDA warning letter by summarizing, validating, and revising it.
        """
        try:
            # Step 1: Summarization by the summarizer agent
            summarization_chat = self.summarizer_agent.initiate_chat(
                self.validator_agent,
                message=content,
                max_turns=self.config.max_turns
            )

            # Extract the assistant's final message from the summarization chat
            summarization_response = self.extract_assistant_response(
                summarization_chat,
                letter_name
            )
            if summarization_response is None:
                return None

            # Parse the summarization response
            summarization_result = self.parse_json_response(
                summarization_response,
                letter_name,
                "summarization"
            )
            if summarization_result is None:
                return None

            # Step 2: Validation loop
            for attempt in range(self.config.max_validation_attempts):
                # Validation by the validator agent
                validation_chat = self.validator_agent.initiate_chat(
                    self.summarizer_agent,
                    message=json.dumps(summarization_result),
                    max_turns=self.config.max_turns
                )

                # Extract the assistant's final message from the validation chat
                validation_response = self.extract_assistant_response(
                    validation_chat,
                    letter_name
                )
                if validation_response is None:
                    return None

                # Parse the validation response
                validation_result = self.parse_json_response(
                    validation_response,
                    letter_name,
                    "validation"
                )
                if validation_result is None:
                    return None

                # Check the validation status
                status = validation_result.get("status") or validation_result.get("validation_status")
                if status == "APPROVED":
                    logging.info(f"Validation approved for {letter_name}.")
                    # Return the approved result immediately to prevent extra steps
                    return {
                        "letter_name": letter_name,
                        "violated_terms": summarization_result.get("violated_terms", []),
                        "recommendations": summarization_result.get("recommendations", []),
                    }
                elif status == "REJECTED":
                    logging.warning(
                        f"Validation rejected for {letter_name} on attempt {attempt + 1}. Revising..."
                    )
                    # Update the summarization result with the revised summary
                    summarization_result = validation_result.get("revised_summary")
                    if not summarization_result:
                        logging.error(f"No revised summary provided for {letter_name}.")
                        return None
                    # Continue to the next validation attempt
                else:
                    logging.error(
                        f"Invalid status in validation result for {letter_name}: {status}"
                    )
                    return None

            # If maximum validation attempts are reached without approval
            logging.error(f"Max validation attempts reached for {letter_name}.")
            return None

        except Exception as e:
            logging.error(f"Error processing letter {letter_name}: {e}")
            return None

    def extract_assistant_response(
        self, chat_result, letter_name: str
    ) -> Optional[str]:
        """
        Extracts the assistant's final message content from the chat history.
        """
        if hasattr(chat_result, "chat_history"):
            for message in reversed(chat_result.chat_history):
                if message["role"] == "assistant":
                    return message["content"]
            logging.error(f"No assistant response found for {letter_name}")
            return None
        else:
            logging.error(f"No chat_history attribute in chat_result for {letter_name}")
            return None

    def parse_json_response(
        self, response_content: str, letter_name: str, stage: str
    ) -> Optional[Dict]:
        """
        Parses the JSON response content from the assistant.
        """
        try:
            # Extract JSON object from the response using regex
            json_match = re.search(r"\{.*\}", response_content, re.DOTALL)
            if json_match:
                json_str = json_match.group()
                return json.loads(json_str)
            else:
                logging.error(
                    f"No JSON object found in {stage} response for {letter_name}: {response_content}"
                )
                return None
        except json.JSONDecodeError as e:
            logging.error(f"Invalid JSON in {stage} response for {letter_name}: {e}")
            return None

    async def cleanup(self):
        """
        Cleans up resources after processing.
        """
        self.logger.info("Cleaning up resources...")