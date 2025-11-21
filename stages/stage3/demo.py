"""
Stage 3 demo: multi-agent workflow with handoffs and shared context.
Run with: python -m stages.stage3.demo
"""

from __future__ import annotations

import asyncio
import sys
from dataclasses import dataclass, field
from pathlib import Path

from agents import (
    Agent,
    ModelSettings,
    RunContextWrapper,
    Runner,
    ToolOutputText,
    function_tool,
)
from agents.mcp import MCPServerStdio, MCPServerStdioParams

from utils.cli import build_verbose_hooks, parse_common_args
from utils.tools.bash import run_bash_command
from utils.ollama_adaptor import model


WORKSPACE_ROOT = Path("/workspace").resolve()
REPO_ROOT = Path(__file__).resolve().parents[2]


@dataclass
class WorkflowState:
    """Shared context that persists across agent handoffs."""

    research_notes: list[str] = field(default_factory=list)
    action_items: list[str] = field(default_factory=list)


def _resolve_relative_path(relative_path: str) -> Path:
    candidate = (WORKSPACE_ROOT / relative_path).resolve()
    if not str(candidate).startswith(str(WORKSPACE_ROOT)):
        msg = f"Path escape blocked for '{relative_path}'."
        raise ValueError(msg)
    return candidate


@function_tool(name_override="workflow.capture_todos")
def capture_todos(
    ctx: RunContextWrapper[WorkflowState],
    relative_path: str,
    limit: int = 5,
) -> ToolOutputText:
    """
    Record TODO/FIXME markers for the shared context and return a formatted snippet.

    Args:
        relative_path: File path relative to the workspace root.
        limit: Maximum number of matches to include.
    """
    try:
        file_path = _resolve_relative_path(relative_path)
    except ValueError as exc:
        return ToolOutputText(text=str(exc))

    if not file_path.is_file():
        return ToolOutputText(text=f"No file found at {relative_path}")

    matches: list[str] = []
    with file_path.open("r", encoding="utf-8") as fh:
        for idx, line in enumerate(fh, start=1):
            if "TODO" in line or "FIXME" in line:
                matches.append(f"L{idx}: {line.strip()}")
            if len(matches) >= limit:
                break

    if not matches:
        return ToolOutputText(text=f"No TODO markers in {relative_path}")

    ctx.context.research_notes.append(
        f"Found {len(matches)} TODO markers in {relative_path}:\n" + "\n".join(matches)
    )

    display = "\n".join(f"- {m}" for m in matches)
    return ToolOutputText(text=f"TODO summary for {relative_path}:\n{display}")


@function_tool(name_override="workflow.save_plan")
def save_plan(
    ctx: RunContextWrapper[WorkflowState],
    steps: list[str],
) -> str:
    """Persist the planner's steps in the shared context."""
    ctx.context.action_items = steps
    return f"Stored {len(steps)} workflow steps."


CURRICULUM_SERVER_PARAMS = MCPServerStdioParams(
    command=sys.executable,
    args=[str(REPO_ROOT / "stages/stage2/mcp_servers/curriculum_server.py")],
    cwd=str(REPO_ROOT),
)


async def main(verbose: bool = False) -> None:
    hooks = build_verbose_hooks(verbose)
    async with MCPServerStdio(
        params=CURRICULUM_SERVER_PARAMS,
        cache_tools_list=True,
        name="Curriculum Server",
    ) as curriculum_server:
        research_agent = Agent(
            name="Research Agent",
            handoff_description="Gathers repository signals and curriculum facts.",
            instructions=(
                "Investigate the repository to find open TODOs and relevant workshop context. "
                "Use the shell tool for quick file inspection and curriculum.fetch_stage_summary via MCP "
                "to enrich your notes. After the tools run, summarise findings for the planner."
            ),
            tools=[capture_todos, run_bash_command],
            mcp_servers=[curriculum_server],
            model=model,
            model_settings=ModelSettings(temperature=0.2),
        )

        planner_agent = Agent(
            name="Planner Agent",
            handoff_description="Transforms research into a concrete workflow plan.",
            instructions=(
                "Read the research summary and design a three-step workflow to improve the repo's Stage 2 assets. "
                "Each step should mention tools or MCP data to reuse. Call workflow.save_plan with the final steps."
            ),
            tools=[save_plan],
            model=model,
            model_settings=ModelSettings(temperature=0.3),
        )

        coordinator = Agent(
            name="Workflow Coordinator",
            instructions=(
                "Coordinate the multi-agent workflow in order:\n"
                "1. Call the Research Agent to gather context.\n"
                "2. Pass its insights to the Planner Agent to create steps.\n"
                "Finally, synthesize a JSON object with keys research and plan summarising the shared context."
            ),
            handoffs=[research_agent, planner_agent],
            model=model,
            model_settings=ModelSettings(temperature=0.05),
        )

        prompt = (
            "We need a Stage 3 workflow that prepares learners for multi-agent collaboration. "
            "Follow the coordination plan."
        )

        state = WorkflowState()
        print("> Running multi-agent workflow...\n")
        result = await Runner.run(coordinator, prompt, context=state, hooks=hooks)

        print("=== Final Coordinator Output ===")
        print(result.final_output)

        print("\n=== Captured Workflow State ===")
        print("- Research notes:")
        for note in state.research_notes:
            print(f"  • {note}")

        print("- Action items:")
        for step in state.action_items:
            print(f"  • {step}")


if __name__ == "__main__":
    args = parse_common_args(__doc__)
    asyncio.run(main(verbose=args.verbose))