"""
Stage 1 demo: custom bash function tool that lets the agent inspect the repo safely.
Run with: python -m stages.stage1.demo
"""

from __future__ import annotations

import asyncio

from agents import Agent, ModelSettings, Runner

from utils.bash_tool import run_bash_command
from utils.cli import build_verbose_hooks, parse_common_args
from utils.ollama_adaptor import model


async def main(verbose: bool = False) -> None:
    hooks = build_verbose_hooks(verbose)
    repo_explorer = Agent(
        name="Bash Repo Explorer",
        instructions=(
            "You are auditing the repository. Use the bash.run tool to execute safe shell commands "
            "such as ls, pwd, cat, head, tail, or stat. Summarise what you inspect and cite the "
            "commands you executed."
        ),
        tools=[run_bash_command],
        model=model,
        model_settings=ModelSettings(temperature=0.25),
    )

    prompt = (
        "Give me a quick project status:\n"
        "1. List the root directories.\n"
        "2. Confirm whether a Dockerfile exists.\n"
        "3. Suggest the next shell command I should run."
    )

    print("> Running Bash Repo Explorer...\n")
    result = await Runner.run(repo_explorer, prompt, hooks=hooks)

    print("\n=== Final Answer ===")
    print(result.final_output)


if __name__ == "__main__":
    args = parse_common_args(__doc__)
    asyncio.run(main(verbose=args.verbose))
