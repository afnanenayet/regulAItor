# File: src/Framework/agents/validation_agent.py

from autogen import ConversableAgent
import os
import json
import logging


class InitiatingAgent(ConversableAgent):
    def __init__(self):
        super().__init__(
            name="InitiatingAgent",
            system_message="""
                            Initiating Agent. Recevied warning letter and template from user.""",
            llm_config={
                "model": os.getenv("OPENAI_MODEL", "gpt-4o"),
                "api_key": os.getenv("OPENAI_API_KEY"),
            },
        )
