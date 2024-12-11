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
            name="Summarizer",
            system_message="""
You are an FDA regulatory expert. Please extract the following types of data from an FDA warning letter:

1. All violated terms/regulations with specific citations. These are usually listed in abbreviated 
   form in the letter, for example, '(21 CFR 211.100(a))'. Sometimes the FDA letter will
   say something like 'Title 21 Code of Federal Regulations, Parts 200 and 211', but you want to extract
   the abbreviated forms if possible. They will usually be in parenthesis. There may be more than one.
   Do not include the outer parenthesis in the output. If you see a regulation listed like this: '(21 U.S.C. 342(a)(2)(C)(i))'
   then the output you want to record is '21 U.S.C. 342(a)(2)(C)(i)'. Normalize the forms so they are easy to search.
2. Recommendations from the FDA to ensure compliance. The FDA will state what the recipient of the warning letter can do
   in order to correct their violations. Capture each recommendation separately.

Return **ONLY** a JSON object with the following format:
{
    "violated_terms": ["...", "..."],
    "recommendations": ["...", "..."]
}

Do not include any additional text outside the JSON object.
""",
            llm_config=self.agent_config.llm_config,
            human_input_mode="NEVER",
        )
        self.validator_agent = ConversableAgent(
            name="Validator",
            system_message="""You are an FDA compliance validator. Your task is to review the summarized extraction against the original letter and decide whether it is acceptable.

Instructions:
1. Verify all violations are captured.
2. Ensure recommendations match violations.
3. Check for missing critical information.

If the summary is acceptable, respond with the following JSON:
{
    "status": "APPROVED",
    "feedback": "Optional feedback or comments."
}

If the summary is not acceptable, respond with the following JSON:
{
    "status": "REJECTED",
    "feedback": "Detailed explanation of issues.",
    "revised_summary": {
        "violated_terms": ["...", "..."],
        "recommendations": ["...", "..."]
    }
}

Return **ONLY** the JSON object and no additional text.
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
            # Initiate the summarization chat
            summarization_chat = self.summarizer_agent.initiate_chat(
                self.validator_agent, message=content, max_turns=self.config.max_turns
            )

            # Extract the assistant's final message from the summarization chat
            summarization_response = self.extract_assistant_response(
                summarization_chat, letter_name
            )
            if summarization_response is None:
                return None

            # Parse the summarization response
            summarization_result = self.parse_json_response(
                summarization_response, letter_name, "summarization"
            )
            if summarization_result is None:
                return None

            # Start the validation loop
            for attempt in range(self.config.max_validation_attempts):
                # Initiate validation
                validation_chat = self.validator_agent.initiate_chat(
                    self.summarizer_agent,
                    message=json.dumps(summarization_result),
                    max_turns=self.config.max_turns,
                )

                # Extract the assistant's final message from the validation chat
                validation_response = self.extract_assistant_response(
                    validation_chat, letter_name
                )
                if validation_response is None:
                    return None

                # Parse the validation response
                validation_result = self.parse_json_response(
                    validation_response, letter_name, "validation"
                )
                if validation_result is None:
                    return None

                # Check validation status
                if validation_result.get("status") == "APPROVED":
                    logging.info(f"Validation approved for {letter_name}.")
                    return {
                        "letter_name": letter_name,
                        "violated_terms": summarization_result.get(
                            "violated_terms", []
                        ),
                        "recommendations": summarization_result.get(
                            "recommendations", []
                        ),
                    }
                elif validation_result.get("status") == "REJECTED":
                    logging.warning(
                        f"Validation rejected for {letter_name} on attempt {attempt + 1}. Revising..."
                    )
                    summarization_result = validation_result.get("revised_summary")
                    if not summarization_result:
                        logging.error(f"No revised summary provided for {letter_name}.")
                        return None
                    # Proceed to the next validation attempt with the revised summary
                else:
                    logging.error(
                        f"Invalid status in validation result for {letter_name}: {validation_result.get('status')}"
                    )
                    return None

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
