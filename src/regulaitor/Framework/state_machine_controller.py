import enum
from typing import Dict, Any
from loguru import logger

from regulaitor.Framework.rag_agent import FDAWarningLetterSystem


class WarningLetterState(enum.Enum):
    """Enumerate states for FDA Warning Letter processing"""

    INIT = "Initialization"
    INPUT_VALIDATION = "Input Validation"
    SUMMARY_EXTRACTION = "Summary Extraction"
    SIMILAR_CASES_RETRIEVAL = "Similar Cases Retrieval"
    REGULATION_EXTRACTION = "Regulation Extraction"
    LAW_CONTENT_RETRIEVAL = "Law Content Retrieval"
    CORRECTIVE_ACTION_GENERATION = "Corrective Action Generation"
    REVIEW_AND_VALIDATION = "Review and Validation"
    FINALIZATION = "Finalization"
    ERROR = "Error State"


class StateMachineController:
    def __init__(self, warning_letter_system: FDAWarningLetterSystem):
        """
        Initialize the State Machine Controller

        :param warning_letter_system: The main FDA Warning Letter System instance
        """
        self.system = warning_letter_system
        self.current_state = WarningLetterState.INIT
        self.state_results: Dict[WarningLetterState, Any] = {}
        self.max_state_transitions = 20
        self.state_transition_count = 0

    def transition_state(self, warning_letter: str) -> Dict[str, Any]:
        """
        State machine logic for processing warning letters

        :param warning_letter: FDA warning letter text
        :return: Processing results dictionary
        """
        while self.current_state != WarningLetterState.FINALIZATION:
            logger.info(f"Current State: {self.current_state.value}")

            if self.state_transition_count >= self.max_state_transitions:
                logger.warning("Maximum state transitions reached")
                break

            # State transition logic
            if self.current_state == WarningLetterState.INIT:
                self.current_state = WarningLetterState.INPUT_VALIDATION

            elif self.current_state == WarningLetterState.INPUT_VALIDATION:
                validation_result = self._input_validation(warning_letter)
                if validation_result:
                    self.current_state = WarningLetterState.SUMMARY_EXTRACTION
                else:
                    self.current_state = WarningLetterState.ERROR

            elif self.current_state == WarningLetterState.SUMMARY_EXTRACTION:
                summary = self._extract_summary(warning_letter)
                self.state_results[WarningLetterState.SUMMARY_EXTRACTION] = summary
                self.current_state = WarningLetterState.SIMILAR_CASES_RETRIEVAL

            elif self.current_state == WarningLetterState.SIMILAR_CASES_RETRIEVAL:
                summary_embedding = self.system.get_embedding(
                    self.state_results[WarningLetterState.SUMMARY_EXTRACTION]
                )
                similar_cases = self._retrieve_similar_cases(summary_embedding)
                self.state_results[WarningLetterState.SIMILAR_CASES_RETRIEVAL] = (
                    similar_cases
                )
                self.current_state = WarningLetterState.REGULATION_EXTRACTION

            elif self.current_state == WarningLetterState.REGULATION_EXTRACTION:
                regulations = self._extract_regulations(warning_letter)
                self.state_results[WarningLetterState.REGULATION_EXTRACTION] = (
                    regulations
                )
                self.current_state = WarningLetterState.LAW_CONTENT_RETRIEVAL

            elif self.current_state == WarningLetterState.LAW_CONTENT_RETRIEVAL:
                law_content = self._retrieve_law_content(
                    self.state_results[WarningLetterState.REGULATION_EXTRACTION]
                )
                self.state_results[WarningLetterState.LAW_CONTENT_RETRIEVAL] = (
                    law_content
                )
                self.current_state = WarningLetterState.CORRECTIVE_ACTION_GENERATION

            elif self.current_state == WarningLetterState.CORRECTIVE_ACTION_GENERATION:
                corrective_actions = self._generate_corrective_actions(
                    warning_letter,
                    self.state_results[WarningLetterState.SIMILAR_CASES_RETRIEVAL],
                    self.state_results[WarningLetterState.LAW_CONTENT_RETRIEVAL],
                )
                self.state_results[WarningLetterState.CORRECTIVE_ACTION_GENERATION] = (
                    corrective_actions
                )
                self.current_state = WarningLetterState.REVIEW_AND_VALIDATION

            elif self.current_state == WarningLetterState.REVIEW_AND_VALIDATION:
                review_result = self._review_corrective_actions(
                    warning_letter,
                    self.state_results[WarningLetterState.CORRECTIVE_ACTION_GENERATION],
                )

                self.state_results[WarningLetterState.REVIEW_AND_VALIDATION] = (
                    review_result
                )

                if review_result.get("approved", "No") == "Yes":
                    self.current_state = WarningLetterState.FINALIZATION
                else:
                    # Retry corrective action generation
                    self.current_state = WarningLetterState.CORRECTIVE_ACTION_GENERATION

            elif self.current_state == WarningLetterState.ERROR:
                break

            self.state_transition_count += 1

        # Prepare final results
        final_results = {
            "state_results": self.state_results,
            "total_transitions": self.state_transition_count,
        }

        return final_results

    def _input_validation(self, warning_letter: str) -> bool:
        """Validate input warning letter"""
        guardrail_check = self.system.input_guardrail(user_input=warning_letter)
        return guardrail_check.should_block == "No"

    def _extract_summary(self, warning_letter: str) -> str:
        """Extract summary using DSPy"""
        summary_prediction = self.system.summary_generator(
            warning_letter=warning_letter
        )
        return summary_prediction.summary

    def _retrieve_similar_cases(self, summary_embedding: list) -> list:
        """Retrieve similar cases based on summary embedding"""
        return self.system.retrieve_similar_cases(summary_embedding)

    def _extract_regulations(self, warning_letter: str) -> list:
        """Extract regulation references"""
        return self.system.regulation_agent.generate_response(warning_letter)

    def _retrieve_law_content(self, regulations: list) -> Any:
        """Retrieve full law content"""
        return self.system.law_provider.generate_response(regulations)

    def _generate_corrective_actions(
        self, warning_letter: str, similar_cases: list, law_content: Any
    ) -> Any:
        """Generate corrective actions"""
        return self.system.corrective_agent.generate_response(
            {
                "warning_letter": warning_letter,
                "similar_cases": similar_cases,
                "law_content": law_content,
            }
        )

    def _review_corrective_actions(
        self, warning_letter: str, corrective_action: Any
    ) -> Dict[str, Any]:
        """Review and validate corrective actions"""
        return self.system.review_agent.generate_response(
            {
                "warning_letter": warning_letter,
                "corrective_action": corrective_action,
            }
        )

    def reset(self):
        """Reset the state machine to initial state"""
        self.current_state = WarningLetterState.INIT
        self.state_results.clear()
        self.state_transition_count = 0
