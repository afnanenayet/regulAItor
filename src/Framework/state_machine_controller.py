# File: Framework/state_machine_controller.py

import enum
from typing import Dict, Any
from loguru import logger

from Framework.RAG.fda_warning_letter_system import FDAWarningLetterSystem  # Updated import

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
        try:
            while self.current_state != WarningLetterState.FINALIZATION:
                logger.info(f"Current State: {self.current_state.value}")

                if self.state_transition_count >= self.max_state_transitions:
                    logger.warning("Maximum state transitions reached")
                    break

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
                    self.state_results[WarningLetterState.SIMILAR_CASES_RETRIEVAL] = similar_cases
                    self.current_state = WarningLetterState.REGULATION_EXTRACTION

                # Add other state transitions as needed...

                elif self.current_state == WarningLetterState.FINALIZATION:
                    break

                self.state_transition_count += 1

            final_results = {
                'state_results': self.state_results,
                'total_transitions': self.state_transition_count
            }

            return final_results

        except Exception as e:
            logger.error(f"State machine error: {e}")
            return {'error': str(e)}

    def _input_validation(self, warning_letter: str) -> bool:
        """Validate input warning letter"""
        guardrail_check = self.system.input_guardrail(user_input=warning_letter)
        return guardrail_check['should_block'] == 'No'

    def _extract_summary(self, warning_letter: str) -> str:
        """Extract summary using the system's summary generator"""
        summary_prediction = self.system.summary_generator(warning_letter=warning_letter)
        return summary_prediction['summary']

    def _retrieve_similar_cases(self, summary_embedding: list) -> list:
        """Retrieve similar cases based on summary embedding"""
        return self.system.retrieve_similar_cases(summary_embedding)

    def reset(self):
        """Reset the state machine to initial state"""
        self.current_state = WarningLetterState.INIT
        self.state_results.clear()
        self.state_transition_count = 0