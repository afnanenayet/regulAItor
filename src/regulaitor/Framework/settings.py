from dataclasses import dataclass
import dspy


class InputGuardrail(dspy.Signature):
    """Signature for input validation"""

    user_input: str = dspy.InputField()
    should_block: str = dspy.OutputField(
        desc="'Yes' if input is not an FDA warning letter, 'No' if it is"
    )
    reason: str = dspy.OutputField(desc="Reason for blocking the input")


class GenerateSummary(dspy.Signature):
    """Signature for generating FDA warning letter summary"""

    warning_letter: str = dspy.InputField()
    summary: str = dspy.OutputField()
