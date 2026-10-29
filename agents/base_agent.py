"""Base Agent architecture for multi-agent workflows."""

import time
from dataclasses import dataclass, field
from typing import Dict, Any, Optional
from sarvam_client import SarvamClient


@dataclass
class AgentResult:
    """Standardized result returned by any agent in the pipeline."""
    agent_name: str
    role: str
    output: str
    execution_time: float
    status: str = "success"
    metadata: Dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None


class BaseAgent:
    """Abstract base class for all specialized agents in the research system."""

    def __init__(
        self,
        name: str,
        role: str,
        description: str,
        system_prompt: str,
        client: Optional[SarvamClient] = None
    ):
        self.name = name
        self.role = role
        self.description = description
        self.system_prompt = system_prompt
        self.client = client or SarvamClient()

    def build_user_prompt(self, context: Dict[str, Any]) -> str:
        """Construct the prompt sent to the LLM based on input context."""
        raise NotImplementedError("Each agent must implement its own build_user_prompt method.")

    def run(self, context: Dict[str, Any]) -> AgentResult:
        """Executes the agent's core task, logging start and end time."""
        start_time = time.time()
        try:
            user_prompt = self.build_user_prompt(context)
            messages = [
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": user_prompt}
            ]
            response = self.client.generate(
                messages=messages,
                agent_role=f"{self.name} - {self.role}"
            )
            elapsed = time.time() - start_time
            return AgentResult(
                agent_name=self.name,
                role=self.role,
                output=response.get("content", ""),
                execution_time=round(elapsed, 2),
                status="success",
                metadata={
                    "model": response.get("model", self.client.model),
                    "usage": response.get("usage", {}),
                    "mode": response.get("mode", "live"),
                }
            )
        except Exception as e:
            elapsed = time.time() - start_time
            return AgentResult(
                agent_name=self.name,
                role=self.role,
                output="",
                execution_time=round(elapsed, 2),
                status="failed",
                error=str(e),
                metadata={"error_details": str(e)}
            )
