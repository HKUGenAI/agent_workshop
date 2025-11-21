"""
Stage 3 Activity: Red Team vs. Blue Team Security Audit.

Objective: Orchestrate an adversarial workflow where a Defender (Blue) and Attacker (Red)
iterate on a configuration until it meets the CISO's standards.

Run with: python -m stages.stage3.activity.starter_workflow
"""

from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from typing import Literal

from agents import (
    Agent,
    ModelSettings,
    RunContextWrapper,
    Runner,
    ToolOutputText,
    function_tool,
)
from pydantic import BaseModel

from utils.cli import build_verbose_hooks, parse_common_args
from utils.ollama_adaptor import model


# --- Shared State ---

@dataclass
class AuditState:
    """Shared context representing the 'battleground'."""
    proposed_config: str = ""
    vulnerabilities: list[str] = field(default_factory=list)
    iteration: int = 0


# --- Final Output Schema ---

class SecurityReport(BaseModel):
    final_config: str
    resolved_issues: list[str]
    approval_status: Literal["APPROVED", "REJECTED"]
    total_iterations: int


# --- Tools ---

@function_tool(name_override="audit.submit_config")
def submit_config(
    ctx: RunContextWrapper[AuditState],
    config_content: str,
    comment: str = "",
) -> ToolOutputText:
    """
    (Blue Team) Propose or update the system configuration.
    """
    ctx.context.proposed_config = config_content
    ctx.context.iteration += 1
    # Clear old vulnerabilities since we are submitting a fix
    old_vulns = len(ctx.context.vulnerabilities)
    ctx.context.vulnerabilities.clear()
    
    return ToolOutputText(
        text=f"Config updated (Iteration {ctx.context.iteration}). Previous vulnerabilities cleared: {old_vulns}. Comment: {comment}"
    )


@function_tool(name_override="audit.report_vulnerability")
def report_vulnerability(
    ctx: RunContextWrapper[AuditState],
    severity: Literal["low", "medium", "high", "critical"],
    description: str,
) -> str:
    """
    (Red Team) Log a security flaw found in the current config.
    """
    entry = f"[{severity.upper()}] {description}"
    ctx.context.vulnerabilities.append(entry)
    return f"Vulnerability logged: {entry}"


# --- Main Workflow ---

async def main(verbose: bool = False) -> None:
    hooks = build_verbose_hooks(verbose)
    state = AuditState()

    # 1. Blue Team: The Defender
    # Responsibility: Create the initial config and fix reported issues.
    blue_agent = Agent(
        name="Blue Team",
        handoff_description="Updates the configuration to fix vulnerabilities.",
        instructions=(
            "You are the System Administrator. Your goal is to secure a web server configuration.\n"
            "1. If the config is empty, propose a basic JSON config (port, debug_mode, admin_user).\n"
            "2. If vulnerabilities are reported, edit the config to fix them (e.g., disable debug, change default ports).\n"
            "3. Always use 'audit.submit_config' to save your changes."
        ),
        tools=[submit_config],
        model=model,
        model_settings=ModelSettings(temperature=0.2),
    )

    # 2. Red Team: The Attacker
    # Responsibility: Find flaws.
    red_agent = Agent(
        name="Red Team",
        handoff_description="Audits the configuration for security flaws.",
        instructions=(
            "You are an Ethical Hacker. Inspect the 'proposed_config' in the context.\n"
            "Look for common mistakes:\n"
            "- Debug mode enabled\n"
            "- Default admin credentials\n"
            "- Insecure ports (e.g., 80 instead of 443)\n"
            "- Missing encryption settings\n"
            "Use 'audit.report_vulnerability' to log EVERY issue you find. If it looks perfect, say 'No issues found'."
        ),
        tools=[report_vulnerability],
        model=model,
        model_settings=ModelSettings(temperature=0.4),
    )

    # 3. CISO: The Coordinator/Judge
    # Responsibility: Decide loop or finish.
    ciso_agent = Agent(
        name="CISO",
        instructions=(
            "You manage the security audit lifecycle.\n"
            "Step 1: Call Blue Team to draft/fix the config.\n"
            "Step 2: Call Red Team to audit the new config.\n"
            "Step 3: Review the state.\n"
            "   - If vulnerabilities exist: Loop back to Step 1 (Blue Team).\n"
            "   - If NO vulnerabilities AND config is not empty: Output the final SecurityReport JSON with status APPROVED.\n"
            "   - Limit to 3 iterations max. If still failing, output REJECTED."
        ),
        handoffs=[blue_agent, red_agent],
        model=model,
        model_settings=ModelSettings(temperature=0.1),
        output_type=SecurityReport,
    )

    print("> Starting Red Team vs. Blue Team Audit...")
    
    # We provide an empty starting prompt because the CISO instructions drive the flow.
    result = await Runner.run(
        ciso_agent, 
        "Secure the web server configuration.", 
        context=state, 
        hooks=hooks
    )

    report = result.final_output_as(SecurityReport)

    print("\n=== Final Security Report ===")
    print(report.model_dump_json(indent=2))
    print(f"\nFinal Config:\n{report.final_config}")


if __name__ == "__main__":
    args = parse_common_args(__doc__)
    asyncio.run(main(verbose=args.verbose))
