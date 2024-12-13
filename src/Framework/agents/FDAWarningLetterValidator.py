import dspy

class FDAWarningLetterValidator(dspy.Module):
    def __call__(self, text):
        # Define a list of key phrases that might indicate FD&C Act violations
        violation_phrases = [
            "violations of the FD&C Act",
            "violation of the Federal Food, Drug, and Cosmetic Act",
            "not in compliance with the FD&C Act",
            "FD&C Act compliance issues",
            "violative under the FD&C Act",
            "contrary to the FD&C Act"
        ]
        
        # Assert that at least one key violation phrase is present
        dspy.Assert(
            any(phrase in text for phrase in violation_phrases),
            "Missing key phrase indicating legal violations under the FD&C Act."
        )
        
        # Assert the presence of FDA identification
        dspy.Assert(
            "Food and Drug Administration" in text or "FDA" in text,
            "Missing FDA identification.",
        )

        # Suggest improvements if necessary
        corrective_phrases = ["corrective action", "corrections", "remediation steps"]
        if not any(phrase in text for phrase in corrective_phrases):
            dspy.Suggest(
                "The letter should clearly state required corrective actions or remediation steps.",
            )
        return True  # If no exception is raised, it is a valid FDA warning letter