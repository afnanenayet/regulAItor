# File: src/Framework/agents/validation_agent.py

from autogen import ConversableAgent
import os
import json
import logging


class Similar_case_Recommendation(ConversableAgent):
    def __init__(self):
        super().__init__(
            name="Similar_case_agent",
            system_message="""
                            Filter out at least 10 similar recommendations from the retrieved cases that align with the violated terms in the original warning letter.             """,
            llm_config={
                "model": os.getenv("OPENAI_MODEL", "gpt-4o"),
                "api_key": os.getenv("OPENAI_API_KEY"),
            },
        )
