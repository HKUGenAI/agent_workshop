# Stage 3 · Multi-Agent Workflow

Now that you can extend a single agent, orchestrate an end-to-end workflow with multiple specialists. Each agent can own a slice of the problem; the coordinator decides how to route tasks and merge results.

## Learning Goals

- Model a multi-step process with cooperating agents and handoffs.
- Maintain lightweight shared context across the workflow.
- Implement **adversarial** or **iterative** loops (e.g. "Reviewer rejects -> Coder fixes").
- Capture structured outputs for downstream automation.

## 1. Concepts Refresher

- **Handoffs** — An agent can delegate to another agent (or a `handoff(...)` wrapper) when it needs help. Provide a `handoff_description` so the coordinator knows when to call it.
- **Coordinator Agent** — The top-level agent that routes work across specialists.
- **Run Context** — Mutable object (`AuditState` in the activity) used to store the evolving artifact (the config) and the critique (vulnerabilities).

## 2. Demo Overview

File: `stages/stage3/demo.py`

A linear workflow: `Coordinator` -> `Research` -> `Planner`.
Run it to see basic delegation:

```bash
python -m stages.stage3.demo --verbose
```

## 3. Activity: Red Team vs. Blue Team

File: `stages/stage3/activity/starter_workflow.py`

We have implemented a "Security Audit" game.

**The Players:**
1.  **Blue Team (Defender):** Drafts a server configuration and applies fixes.
2.  **Red Team (Attacker):** Inspects the configuration for flaws (e.g. debug mode, weak ports) and reports them.
3.  **CISO (Judge):** Routes the work. If the Red Team finds bugs, the CISO sends the config back to the Blue Team. If it's clean, the CISO approves it.

**Your Goal:**
The starter code is fully functional but basic. Try to improve it:
1.  **Run it first:** `python -m stages.stage3.activity.starter_workflow`
2.  **Make it harder:** Edit the `Red Team` instructions to be pickier (e.g., require specific headers or strict TLS versions).
3.  **Make it smarter:** Give the `Blue Team` a "Knowledge Base" tool (maybe connect the MCP server?) to look up secure defaults so it makes fewer mistakes.
4.  **Add a limit:** Ensure the CISO kills the process after 5 loops if they can't agree.

**Stretch ideas**
- Add a "Cost" tracker to the state. Each fix adds 'cost'. The CISO rejects if it gets too expensive.
- Save the final approved JSON to a real file `secure_server.json`.

Congrats! You've built a self-correcting multi-agent system.
