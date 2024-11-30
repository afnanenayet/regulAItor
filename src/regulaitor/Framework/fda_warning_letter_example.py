from pathlib import Path
import sys

import click
from click_help_colors import HelpColorsGroup
from loguru import logger
import rich.traceback

from regulaitor.Framework.rag_agent import FDAWarningLetterSystem
from regulaitor.Framework.state_machine_controller import StateMachineController


@click.group(
    cls=HelpColorsGroup,
    help_headers_color="yellow",
    help_options_color="green",
    help_options_custom_colors={"command3": "red", "command4": "cyan"},
)
def cli():
    pass


@cli.command()
@click.argument(
    "config_file",
    type=click.Path(exists=True, file_okay=True, dir_okay=False, path_type=Path),
)
@click.argument(
    "warning_letter",
    type=click.Path(exists=True, file_okay=True, dir_okay=False, path_type=Path),
)
def warning_letter_example(config_file: Path, warning_letter: Path) -> None:
    """
    Main entry point for FDA Warning Letter Processing System
    Demonstrates usage of the state machine controller

    CONFIG_FILE is the path to your JSON file containing your OpenAI API credentials.

    WARNING_LETTER is a file path to a text file with the contents of an FDA warning letter.
    """
    _ = rich.traceback.install(suppress=[click])

    # Initialize the FDA Warning Letter System
    fda_system = FDAWarningLetterSystem(config_file)

    # Initialize State Machine Controller
    state_machine = StateMachineController(fda_system)

    # Sample Warning Letter (replace with actual input mechanism)
    WARNING_LETTER = """[Insert actual FDA warning letter content here]"""

    logger.info("Starting FDA Warning Letter Processing...")

    # Process Warning Letter using State Machine
    results = state_machine.transition_state(warning_letter.read_text())

    # Display Results
    print("\nProcessing Results:")
    for state, result in results.get("state_results", {}).items():
        print(f"{state.value}: {result}")

    print(f"\nTotal State Transitions: {results.get('total_transitions', 0)}")

    # Reset system state
    state_machine.reset()


if __name__ == "__main__":
    warning_letter_example()
