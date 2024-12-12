# File: Framework/main.py

import sys
from loguru import logger

from Framework.RAG.fda_warning_letter_system import FDAWarningLetterSystem  # Updated import
from Framework.state_machine_controller import StateMachineController

def main():
    """
    Main entry point for FDA Warning Letter Processing System
    Demonstrates usage of the state machine controller
    """
    try:
        # Initialize the FDA Warning Letter System
        fda_system = FDAWarningLetterSystem()
        fda_system.prepare_data()  # Prepare data before processing

        # Initialize State Machine Controller
        state_machine = StateMachineController(fda_system)

        # Sample Warning Letter (replace with actual input mechanism)
        WARNING_LETTER = """[Insert actual FDA warning letter content here]"""

        logger.info("Starting FDA Warning Letter Processing...")

        # Process Warning Letter using State Machine
        results = state_machine.transition_state(WARNING_LETTER)

        # Display Results
        print("\nProcessing Results:")
        for state, result in results.get('state_results', {}).items():
            print(f"{state.value}: {result}")

        print(f"\nTotal State Transitions: {results.get('total_transitions', 0)}")

    except Exception as e:
        logger.error(f"Error in main processing: {e}")
        sys.exit(1)
    finally:
        # Reset system state
        state_machine.reset()

if __name__ == "__main__":
    main()
