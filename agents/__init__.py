"""Multi-agent package for AI research assistant."""
from .base_agent import BaseAgent, AgentResult
from .research_agent import ResearchAgent
from .analysis_agent import AnalysisAgent
from .verification_agent import VerificationAgent
from .writer_agent import WriterAgent
from .coordinator import CoordinatorAgent, WorkflowExecutionState

__all__ = [
    "BaseAgent",
    "AgentResult",
    "ResearchAgent",
    "AnalysisAgent",
    "VerificationAgent",
    "WriterAgent",
    "CoordinatorAgent",
    "WorkflowExecutionState",
]
