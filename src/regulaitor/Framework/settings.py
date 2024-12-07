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
    """
    Read the FDA warning letter and extract a one-paragraph summary that lists:

        1. All violated terms and regulations (with specific references)
        2. Compliance issues alleged in the document
        3. Brief description of each violation
        4. Impact on pharmaceutical standards compliance

    Make the summary concise yet comprehensive, capturing all key compliance failures.
    """

    warning_letter: str = dspy.InputField()
    summary: str = dspy.OutputField()
