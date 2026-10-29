"""Automated tests for the Sarvam AI Multi-Agent Research System."""

import unittest
from pathlib import Path
from sarvam_client import SarvamClient
from tools.search_tool import KnowledgeRetriever
from agents.research_agent import ResearchAgent
from agents.analysis_agent import AnalysisAgent
from agents.verification_agent import VerificationAgent
from agents.writer_agent import WriterAgent
from agents.coordinator import CoordinatorAgent


class TestMultiAgentSystem(unittest.TestCase):
    """Test suite verifying agent creation, tool retrieval, and end-to-end pipeline."""

    @classmethod
    def setUpClass(cls):
        # Use demo client to test logic without consuming live API tokens
        cls.client = SarvamClient(demo_mode=True)
        cls.test_topic = "Artificial Intelligence applications in healthcare and autonomous systems."

    def test_01_knowledge_retriever(self):
        """Verify Wikipedia knowledge retrieval tool."""
        res = KnowledgeRetriever.gather_background_context("Artificial Intelligence", max_articles=2)
        self.assertIn("sources", res)
        self.assertGreater(len(res["sources"]), 0)
        first = res["sources"][0]
        self.assertTrue(len(first.get("title", "")) > 0)
        self.assertTrue(len(first.get("summary", "")) > 0)

    def test_02_research_agent(self):
        """Verify Agent 1 (Research Agent) produces structured findings."""
        agent = ResearchAgent(client=self.client)
        context = {"topic": self.test_topic}
        result = agent.run(context)
        self.assertEqual(result.status, "success")
        self.assertEqual(result.agent_name, "Research Agent")
        self.assertIn("Definition", result.output)
        self.assertIn("Application", result.output)

    def test_03_analysis_agent(self):
        """Verify Agent 2 (Analysis Agent) generates strategic insights."""
        agent = AnalysisAgent(client=self.client)
        context = {
            "topic": self.test_topic,
            "research_output": "AI systems automate cognitive tasks and assist medical diagnostics."
        }
        result = agent.run(context)
        self.assertEqual(result.status, "success")
        self.assertEqual(result.agent_name, "Analysis Agent")
        self.assertIn("Analytical Synthesis", result.output)

    def test_04_verification_agent(self):
        """Verify Agent 3 (Verification Agent) creates audit scorecard."""
        agent = VerificationAgent(client=self.client)
        context = {
            "topic": self.test_topic,
            "research_output": "AI diagnostic models achieved high clinical accuracy.",
            "analysis_output": "High impact expected in healthcare.",
            "retrieved_sources": []
        }
        result = agent.run(context)
        self.assertEqual(result.status, "success")
        self.assertEqual(result.agent_name, "Verification Agent")
        self.assertIn("Scorecard", result.output)

    def test_05_writer_agent(self):
        """Verify Agent 4 (Writer Agent) produces publication report."""
        agent = WriterAgent(client=self.client)
        context = {
            "topic": self.test_topic,
            "research_output": "Research facts...",
            "analysis_output": "Analysis insights...",
            "verification_output": "Verification directives..."
        }
        result = agent.run(context)
        self.assertEqual(result.status, "success")
        self.assertEqual(result.agent_name, "Writer Agent")
        self.assertIn("Executive Summary", result.output)

    def test_06_coordinator_workflow(self):
        """Verify Coordinator Agent runs full 4-agent workflow and saves report."""
        output_dir = Path(__file__).resolve().parent / "test_reports"
        coordinator = CoordinatorAgent(client=self.client, output_dir=str(output_dir))
        
        state = coordinator.run_workflow(topic="Explain quantum computing and its security impact.")
        self.assertTrue(state.is_successful)
        self.assertEqual(state.status, "completed")
        self.assertEqual(len(state.agent_results), 4)
        self.assertTrue(len(state.final_report) > 100)

        # Check saved report file
        files = list(output_dir.glob("*.md"))
        self.assertGreater(len(files), 0)

        # Clean up test output directory
        for f in files:
            try:
                f.unlink()
            except Exception:
                pass
        try:
            output_dir.rmdir()
        except Exception:
            pass


if __name__ == "__main__":
    unittest.main()
