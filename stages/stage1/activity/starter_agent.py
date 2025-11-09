"""
Stage 1 activity starter.

Goal: build a write-enabled agent that implements the task in
`stages/stage1/activity/code_task.py` using a custom write tool.
Run with: python -m stages.stage1.activity.starter_agent --verbose
"""

from __future__ import annotations

import asyncio

from agents import Agent, ModelSettings, Runner

from utils.tools import run_bash_command, read_text_file, write_text_file
from utils.cli import build_verbose_hooks, parse_common_args
from utils.ollama_adaptor import model

TASK_FILE = "stages/stage1/activity/code_task.py"

async def run_activity(verbose: bool = False) -> None:
    hooks = build_verbose_hooks(verbose)
    write_agent = Agent(
        name="Workshop Write Coach",
        instructions=(
            "You finish coding chores inside this repository.\n"
            f"Focus file: `{TASK_FILE}`. Implement `format_stage_report` to match the\n"
            "spec in that file by calling the provided tools.\n\n"
            "Workflow:\n"
            f"1. Use `read.file`\n"
            "   (with optional line ranges) to read the task and gather any additional\n"
            "   context you need.\n"
            "2. Outline your plan before editing so the reviewer understands your\n"
            "   approach.\n"
            "3. Call `write.file` with the `start_line`/`end_line` parameters to perform\n"
            "   targeted replacements inside the file.\n"
            "4. Verify the change by re-reading the file\n"
            "5. In your final response, summarize what you changed and cite the specific\n"
            "   commands/tools that informed your work."
        ),
        tools=[
            run_bash_command,
            read_text_file,
            write_text_file,
        ],
        model=model,
        model_settings=ModelSettings(temperature=0.2),
    )

    result = await Runner.run(
        write_agent,
        (
            "Use the read.file and write.file tools to implement format_stage_report in "
            f"{TASK_FILE}, then explain how the result satisfies the requirements."
        ),
        hooks=hooks,
        max_turns=50,
    )
    print("\n=== Agent Report ===")
    print(result.final_output)


if __name__ == "__main__":
    args = parse_common_args(__doc__)
    asyncio.run(run_activity(verbose=args.verbose))
