# File: Framework/RAG/regulation_extraction_agent.py

import re

class RegulationExtractionAgent:
    def extract_regulations(self, warning_letter: str) -> list:
        """
        Extracts violated regulation citations from an FDA warning letter.

        :param warning_letter: The text of the FDA warning letter.
        :return: A list of extracted regulation citations.
        """
        # Regex pattern to match CFR citations (e.g., "21 CFR 211.22")
        pattern = r"(21\s*CFR\s*\d+(?:\.\d+)*(?:\(\w+\))*)"
        matches = re.findall(pattern, warning_letter, re.IGNORECASE)
        # Normalize and remove duplicates
        extracted_regulations = list(set(match.strip() for match in matches))
        return extracted_regulations
