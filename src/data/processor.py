# processor.py

from openai import OpenAI
import json
import asyncio
from typing import Dict, Optional
import logging
from config import ProcessorConfig, AgentConfig
from rate_limiter import RateLimiter

class FDALetterProcessor:
    def __init__(self, config: ProcessorConfig):
        self.config = config
        self.agent_config = AgentConfig()
        self.rate_limiter = RateLimiter(config.rate_limit_per_minute)
        self.setup_logging()
        self.client = OpenAI(api_key=self.agent_config.api_key)
        self.agent_logger = logging.getLogger('agent_interaction')

      

    def setup_logging(self):
        # Main application logger
        logging.basicConfig(
            level=self.config.log_level,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('fda_processor.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
        # Agent interaction logger
        self.agent_logger = logging.getLogger('agent_interaction')
        agent_handler = logging.StreamHandler()
        agent_handler.setFormatter(logging.Formatter(
            '\n=== Agent Interaction ===\n%(message)s\n=====================\n'
        ))
        self.agent_logger.addHandler(agent_handler)
        self.agent_logger.setLevel(logging.INFO)

    # Update the call_agent method
    async def call_agent(self, system_message: str, user_message: str) -> str:
        """
        Calls the OpenAI API with the provided system and user messages.
        """
        retries = 0
        while retries < self.agent_config.max_retries:
            try:
                # Log the interaction
                self.agent_logger.info(
                    f"REQUEST:\n"
                    f"System: {system_message}\n"
                    f"User: {user_message}"
                )
                
                response = self.client.chat.completions.create(
                    model=self.agent_config.model,
                    messages=[
                        {"role": "system", "content": system_message},
                        {"role": "user", "content": user_message}
                    ],
                    temperature=self.agent_config.temperature
                )
                
                response_content = response.choices[0].message.content
                
                # Log the response
                self.agent_logger.info(
                    f"RESPONSE:\n{response_content}"
                )
                
                return response_content
                
            except Exception as e:
                self.logger.error(f"Error calling OpenAI API: {e}")
                retries += 1
                await asyncio.sleep(self.agent_config.retry_delay)
        raise Exception("Max retries exceeded when calling OpenAI API.")

    def _parse_response(self, response: str) -> Dict:
        """
        Parses the response and extracts JSON content.
        """
        try:
            # Remove markdown code block markers if present
            response = response.replace('```json', '').replace('```', '').strip()
            return json.loads(response)
        except json.JSONDecodeError as e:
            logging.error(f"JSON decode error: {e}. Response: {response}")
            return {}
        except Exception as e:
            logging.error(f"Unexpected error during parsing: {e}. Response: {response}")
            return {}

    async def summarize_and_validate(self, letter_name: str, content: str) -> Optional[Dict]:
        """
        Summarizes and validates the given FDA warning letter.
        """
        try:
            # Summarization
            await self.rate_limiter.acquire()
            summarizer_system_message = (
                "You are an FDA regulatory expert. Summarize the following warning letter, extracting:\n"
                "1. Violated terms/regulations.\n"
                "2. Recommended corrective steps.\n"
                "Respond only in valid JSON format with the following structure:\n"
                "{\n"
                '  "violated_terms": [list of violated terms],\n'
                '  "recommendations": [list of recommendations]\n'
                "}"
            )
            summary_response = await self.call_agent(
                summarizer_system_message,
                content
            )
            summary = self._parse_response(summary_response)

            if not summary:
                logging.error(f"Failed to parse summarizer response for {letter_name}.")
                return None

            # Validation
            validation_result = await self.validate_summary(summary, content)

            if validation_result.get("status") == "APPROVED":
                return {
                    "letter_name": letter_name,
                    "violated_terms": summary.get("violated_terms", []),
                    "recommendations": summary.get("recommendations", [])
                }
            else:
                logging.warning(f"Validation failed for {letter_name}. Attempting revisions.")
                return await self.revise_summary(letter_name, content, summary, validation_result)

        except Exception as e:
            logging.error(f"Error in summarize_and_validate: {e}")
            return None

    async def validate_summary(self, summary: Dict, content: str) -> Dict:
        """
        Validates the summarized output against the original content.
        """
        try:
            await self.rate_limiter.acquire()
            validator_system_message = (
                "You are an evaluation expert. Verify the summarized output by performing the following checks:\n"
                "1. Confirm all violated terms are correctly extracted.\n"
                "2. Ensure recommendations are accurate and correspond to the violations.\n"
                "3. Validate the response is in proper JSON format.\n"
                "4. Confirm no critical information is missing.\n"
                "Respond only in valid JSON format with the following structure:\n"
                "{\n"
                '  "status": "APPROVED" or "REVISION_NEEDED",\n'
                '  "issues": [list of specific issues if status is "REVISION_NEEDED"],\n'
                '  "suggestions": [list of improvements if status is "REVISION_NEEDED"]\n'
                "}"
            )
            validation_prompt = (
                f"Summary to validate:\n{json.dumps(summary, indent=2)}\n\n"
                f"Original FDA warning letter content:\n{content}"
            )
            validation_response = await self.call_agent(
                validator_system_message,
                validation_prompt
            )
            validation_result = self._parse_response(validation_response)
            return validation_result if validation_result else {"status": "ERROR"}
        except Exception as e:
            logging.error(f"Error during validation: {e}")
            return {"status": "ERROR"}

    async def revise_summary(self, letter_name: str, content: str, summary: Dict, validation_result: Dict) -> Optional[Dict]:
        """
        Handles revision attempts for failed validations.
        """
        for attempt in range(self.config.max_validation_attempts):
            try:
                logging.info(f"Revision attempt {attempt + 1} for {letter_name}.")
                revision_system_message = (
                    "You are an FDA regulatory expert. Revise the summary based on the validation feedback.\n"
                    "Ensure that the revised summary addresses all issues and follows the correct structure.\n"
                    "Respond only in valid JSON format with the following structure:\n"
                    "{\n"
                    '  "violated_terms": [list of violated terms],\n'
                    '  "recommendations": [list of recommendations]\n'
                    "}"
                )
                revision_prompt = (
                    f"Validation feedback:\n{json.dumps(validation_result, indent=2)}\n\n"
                    f"Original FDA warning letter content:\n{content}"
                )
                await self.rate_limiter.acquire()
                revised_summary_response = await self.call_agent(
                    revision_system_message,
                    revision_prompt
                )
                revised_summary = self._parse_response(revised_summary_response)

                if not revised_summary:
                    logging.error(f"Failed to parse summarizer response during revision for {letter_name}.")
                    continue

                # Re-validate the revised summary
                validation_result = await self.validate_summary(revised_summary, content)
                if validation_result.get("status") == "APPROVED":
                    logging.info(f"Revision successful for {letter_name}.")
                    return {
                        "letter_name": letter_name,
                        "violated_terms": revised_summary.get("violated_terms", []),
                        "recommendations": revised_summary.get("recommendations", [])
                    }
            except Exception as e:
                logging.error(f"Error during revision attempt {attempt + 1} for {letter_name}: {e}")
                continue

        logging.error(f"All {self.config.max_validation_attempts} revision attempts failed for {letter_name}.")
        return None

    async def cleanup(self):
        """
        Cleans up any resources used during processing.
        """
        self.logger.info("Cleaning up resources...")