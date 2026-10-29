"""Command Line Interface for the Sarvam AI Multi-Agent Research System.

Executes the 4-agent workflow with rich terminal visualization.
"""

import sys
import io
import argparse
from pathlib import Path

# Ensure UTF-8 output encoding on Windows consoles
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.markdown import Markdown
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn

from config import Config
from sarvam_client import SarvamClient
from agents.coordinator import CoordinatorAgent
from agents.base_agent import AgentResult

console = Console(force_terminal=True)


def render_banner():
    """Display system banner and agent topology."""
    workflow_art = """
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
    console.print(
        Panel(
            f"[bold cyan]AI Research Assistant - Multi-Agent System[/bold cyan]\n"
            f"[dim]Powered by Sarvam AI Models (e.g. sarvam-105b)[/dim]\n"
            f"[yellow]{workflow_art}[/yellow]\n"
            f"[green]* Agent 1: Research Agent[/green] - Collects factual information & structures findings\n"
            f"[green]* Agent 2: Analysis Agent[/green] - Extracts patterns & performs multi-sector critical analysis\n"
            f"[green]* Agent 3: Verification Agent[/green] - Audits evidence, fact-checks & directs corrections\n"
            f"[green]* Agent 4: Writer Agent[/green] - Synthesizes verified findings into an authoritative report\n"
            f"[green]* Coordinator Agent[/green] - Orchestrates data passing, timings & final assembly",
            title="[bold magenta]SARVAM AI MULTI-AGENT ARCHITECTURE[/bold magenta]",
            border_style="magenta",
            expand=False
        )
    )


def run_cli():
    parser = argparse.ArgumentParser(description="Multi-Agent Research Assistant powered by Sarvam AI")
    parser.add_argument(
        "--topic", "-t",
        type=str,
        default="Research Artificial Intelligence and explain its applications.",
        help="Research topic or instruction to process"
    )
    parser.add_argument(
        "--api-key", "-k",
        type=str,
        default=None,
        help="Sarvam AI API subscription key (overrides .env)"
    )
    parser.add_argument(
        "--model", "-m",
        type=str,
        default=Config.SARVAM_MODEL,
        help="Sarvam model to use (default: sarvam-105b)"
    )
    parser.add_argument(
        "--demo", "-d",
        action="store_true",
        help="Force run in demo simulation mode without making live API calls"
    )
    parser.add_argument(
        "--interactive", "-i",
        action="store_true",
        help="Interactively prompt for research topic in terminal"
    )

    args = parser.parse_args()

    render_banner()

    topic = args.topic
    if args.interactive:
        topic_input = console.input("\n[bold yellow]Enter your research topic/question:[/bold yellow] ").strip()
        if topic_input:
            topic = topic_input

    api_key = args.api_key or Config.SARVAM_API_KEY
    demo_mode = args.demo or (not Config.has_api_key() and not args.api_key)

    console.print(f"\n[bold white]Initializing Multi-Agent Workflow...[/bold white]")
    console.print(f"[cyan]• Research Topic:[/cyan] {topic}")
    console.print(f"[cyan]• Engine Model:[/cyan] {args.model}")
    if demo_mode:
        console.print("[yellow]• Mode: DEMO SIMULATION (No active Sarvam key detected. Set SARVAM_API_KEY in .env for live API calls)[/yellow]\n")
    else:
        console.print("[green]• Mode: LIVE SARVAM AI API[/green]\n")

    # Initialize Sarvam Client and Coordinator
    client = SarvamClient(
        api_key=api_key,
        model=args.model,
        demo_mode=demo_mode
    )
    coordinator = CoordinatorAgent(client=client)

    # Multi-agent step tracking
    with Progress(
        SpinnerColumn(spinner_name="dots"),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TimeElapsedColumn(),
        console=console,
        transient=False,
    ) as progress:

        task = progress.add_task("[bold cyan]Executing multi-agent research pipeline...", total=4)

        def on_step_start(name: str, role: str, step: int, total: int):
            progress.update(task, description=f"[bold yellow]Step {step}/{total}:[/bold yellow] [bold white]{name}[/bold white] is executing ({role})...")

        def on_step_complete(res: AgentResult, step: int, total: int):
            progress.advance(task, 1)
            console.print(
                f"[bold green]✓ Step {step}/{total} Complete:[/bold green] "
                f"[white]{res.agent_name}[/white] finished in [cyan]{res.execution_time}s[/cyan]"
            )

        execution_state = coordinator.run_workflow(
            topic=topic,
            on_step_start=on_step_start,
            on_step_complete=on_step_complete,
        )

    if not execution_state.is_successful:
        console.print(f"\n[bold red]Pipeline failed![/bold red] Errors: {execution_state.errors}")
        sys.exit(1)

    # Display Execution Summary Table
    table = Table(title="Multi-Agent Pipeline Execution Summary", border_style="cyan")
    table.add_column("Agent", style="bold white")
    table.add_column("Role", style="dim")
    table.add_column("Execution Time", style="cyan")
    table.add_column("Status", style="green")

    for key, res in execution_state.agent_results.items():
        table.add_row(res.agent_name, res.role, f"{res.execution_time}s", "Completed")

    table.add_row("[bold]Total Pipeline[/bold]", "End-to-End Orchestration", f"[bold]{execution_state.total_duration}s[/bold]", "[bold green]Success[/bold green]")
    console.print("\n")
    console.print(table)

    # Ask or directly render the final report
    console.print("\n" + "=" * 80)
    console.print(Panel("[bold green]FINAL RESEARCH REPORT[/bold green]", border_style="green"))
    console.print(Markdown(execution_state.final_report))
    console.print("=" * 80)

    # Notice of saved file
    saved_path = coordinator.save_report(execution_state)
    console.print(f"\n[bold cyan]Full Multi-Agent Research Dossier Saved to:[/bold cyan] [underline]{saved_path}[/underline]\n")


if __name__ == "__main__":
    run_cli()
