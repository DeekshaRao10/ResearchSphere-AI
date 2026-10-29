"""Coordinator Agent: The Orchestrator for Multi-Agent Workflow.

Assigns tasks, routes data between agents, monitors execution state,
and compiles the final comprehensive research package.
"""

import time
import re
from pathlib import Path
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass, field

from sarvam_client import SarvamClient
from agents.base_agent import AgentResult
from agents.research_agent import ResearchAgent
from agents.analysis_agent import AnalysisAgent
from agents.verification_agent import VerificationAgent
from agents.writer_agent import WriterAgent


@dataclass
class WorkflowExecutionState:
    """Encapsulates the state and artifacts of a multi-agent workflow execution."""
    topic: str
    status: str = "initialized"
    start_time: float = field(default_factory=time.time)
    end_time: Optional[float] = None
    total_duration: float = 0.0
    agent_results: Dict[str, AgentResult] = field(default_factory=dict)
    final_report: str = ""
    errors: List[str] = field(default_factory=list)

    @property
    def is_successful(self) -> bool:
        return self.status == "completed" and bool(self.final_report)


class CoordinatorAgent:
    """Orchestrates the 4-agent research workflow powered by Sarvam AI.
    
    Workflow Topology:
              USER
                |
                v
         COORDINATOR AGENT
                |
         Assigns the tasks
                |
        +-------+-------+
        |               |
        v               v
   RESEARCH AGENT   ANALYSIS AGENT
        |               |
        +-------+-------+
                |
                v
         VERIFICATION AGENT
                |
                v
           WRITER AGENT
                |
                v
          FINAL REPORT
    """

    def __init__(
        self,
        client: Optional[SarvamClient] = None,
        output_dir: Optional[str] = None
    ):
        self.client = client or SarvamClient()
        self.output_dir = Path(output_dir) if output_dir else Path(__file__).resolve().parent.parent / "reports"
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Initialize the 4 specialized agents with shared client
        self.research_agent = ResearchAgent(client=self.client)
        self.analysis_agent = AnalysisAgent(client=self.client)
        self.verification_agent = VerificationAgent(client=self.client)
        self.writer_agent = WriterAgent(client=self.client)

    def run_workflow(
        self,
        topic: str,
        on_step_start: Optional[Callable[[str, str, int, int], None]] = None,
        on_step_complete: Optional[Callable[[AgentResult, int, int], None]] = None,
    ) -> WorkflowExecutionState:
        """Execute the full end-to-end multi-agent research pipeline.
        
        Args:
            topic: The research query or instruction from the user.
            on_step_start: Optional callback(agent_name, role, current_step, total_steps)
            on_step_complete: Optional callback(agent_result, current_step, total_steps)
        """
        state = WorkflowExecutionState(topic=topic, status="running")
        total_steps = 4
        pipeline_context: Dict[str, Any] = {"topic": topic}

        # ---------------------------------------------------------
        # Step 1: Research Agent
        # ---------------------------------------------------------
        step_idx = 1
        if on_step_start:
            on_step_start(self.research_agent.name, self.research_agent.role, step_idx, total_steps)
        
        res_research = self.research_agent.run(pipeline_context)
        state.agent_results["research"] = res_research
        if res_research.status == "failed":
            state.status = "failed"
            state.errors.append(f"Research Agent failed: {res_research.error}")
            return self._finalize_state(state)
        
        pipeline_context["research_output"] = res_research.output
        pipeline_context["retrieved_sources"] = res_research.metadata.get("retrieved_sources", [])
        if on_step_complete:
            on_step_complete(res_research, step_idx, total_steps)

        # ---------------------------------------------------------
        # Step 2: Analysis Agent
        # ---------------------------------------------------------
        step_idx = 2
        if on_step_start:
            on_step_start(self.analysis_agent.name, self.analysis_agent.role, step_idx, total_steps)
        
        res_analysis = self.analysis_agent.run(pipeline_context)
        state.agent_results["analysis"] = res_analysis
        if res_analysis.status == "failed":
            state.status = "failed"
            state.errors.append(f"Analysis Agent failed: {res_analysis.error}")
            return self._finalize_state(state)

        pipeline_context["analysis_output"] = res_analysis.output
        if on_step_complete:
            on_step_complete(res_analysis, step_idx, total_steps)

        # ---------------------------------------------------------
        # Step 3: Verification Agent
        # ---------------------------------------------------------
        step_idx = 3
        if on_step_start:
            on_step_start(self.verification_agent.name, self.verification_agent.role, step_idx, total_steps)
        
        res_verification = self.verification_agent.run(pipeline_context)
        state.agent_results["verification"] = res_verification
        if res_verification.status == "failed":
            state.status = "failed"
            state.errors.append(f"Verification Agent failed: {res_verification.error}")
            return self._finalize_state(state)

        pipeline_context["verification_output"] = res_verification.output
        if on_step_complete:
            on_step_complete(res_verification, step_idx, total_steps)

        # ---------------------------------------------------------
        # Step 4: Writer Agent
        # ---------------------------------------------------------
        step_idx = 4
        if on_step_start:
            on_step_start(self.writer_agent.name, self.writer_agent.role, step_idx, total_steps)
        
        res_writer = self.writer_agent.run(pipeline_context)
        state.agent_results["writer"] = res_writer
        if res_writer.status == "failed":
            state.status = "failed"
            state.errors.append(f"Writer Agent failed: {res_writer.error}")
            return self._finalize_state(state)

        state.final_report = res_writer.output
        state.status = "completed"
        if on_step_complete:
            on_step_complete(res_writer, step_idx, total_steps)

        return self._finalize_state(state)

    def _finalize_state(self, state: WorkflowExecutionState) -> WorkflowExecutionState:
        """Compute final timing and auto-save the generated report."""
        state.end_time = time.time()
        state.total_duration = round(state.end_time - state.start_time, 2)
        if state.is_successful:
            self.save_report(state)
        return state

    def save_report(self, state: WorkflowExecutionState) -> Path:
        """Saves the final report and multi-agent dossier to the output directory."""
        # Sanitize topic for filename
        safe_topic = re.sub(r'[^a-zA-Z0-9_\- ]', '', state.topic).strip()
        safe_topic = re.sub(r'\s+', '_', safe_topic)[:50] or "research_report"
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        filename = f"{safe_topic}_{timestamp}.md"
        file_path = self.output_dir / filename

        report_content = (
            f"# Multi-Agent Research Dossier\n\n"
            f"- **Research Query:** {state.topic}\n"
            f"- **Execution Time:** {state.total_duration} seconds\n"
            f"- **Engine / Model:** {self.client.model}\n"
            f"- **Engine Mode:** {self.client.demo_mode and 'Demo Mode (Simulation)' or 'Live Sarvam AI'}\n\n"
            f"{state.final_report}\n\n"
            f"---\n\n"
            f"## Multi-Agent Execution Appendix\n\n"
        )
        for key in ["research", "analysis", "verification"]:
            res = state.agent_results.get(key)
            if res:
                report_content += (
                    f"### Intermediate Artifact: {res.agent_name} ({res.role})\n"
                    f"- Execution time: {res.execution_time}s\n\n"
                    f"{res.output}\n\n"
                    f"---\n\n"
                )

        file_path.write_text(report_content, encoding="utf-8")
        return file_path
