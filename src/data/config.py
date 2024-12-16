# config.py

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict
import logging
from dotenv import load_dotenv

load_dotenv()

@dataclass
class ProcessorConfig:
    input_dir: Path
    output_dir: Path
    max_validation_attempts: int = 1
    batch_size: int = 5
    timeout_seconds: int = 300
    cache_enabled: bool = True
    log_level: int = logging.INFO
    rate_limit_per_minute: int = 20
    max_turns: int = 3  

@dataclass
class AgentConfig:
    api_key: str = field(default_factory=lambda: os.getenv("OPENAI_API_KEY"))
    model: str = "gpt-4o-mini"  
    temperature: float = 0.2
    max_retries: int = 3
    retry_delay: int = 1

    @property
    def llm_config(self) -> Dict:
        if not self.api_key:
            raise ValueError("API key not found in environment variables")
        return {
            "model": self.model,
            "api_key": self.api_key,
            "temperature": self.temperature
        }