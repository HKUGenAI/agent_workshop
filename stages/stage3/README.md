# Stage 3 · Multi-Agent Workflow

Now that you can extend a single agent, orchestrate an end-to-end workflow with multiple specialists. Each agent can own a slice of the problem; the coordinator decides how to route tasks and merge results.

## Learning Goals

- Model a multi-step process with cooperating agents and handoffs.
- Maintain lightweight shared context across the workflow.
- Implement **adversarial** or **iterative** loops (e.g. "Reviewer rejects -> Coder fixes").
- interact with real files on disk as a shared medium.

## 1. Concepts

- **Handoffs** — An agent can delegate to another agent (or a `handoff(...)` wrapper) when it needs help. Provide a `handoff_description` so the coordinator knows when to call it.
- **Coordinator Agent** — The top-level agent that routes work across specialists.
- **Run Context** — Mutable object (`AuditState` in the activity) used to store the evolving state (vulnerabilities found, iteration count).

## 2. Demo Overview

File: `stages/stage3/demo.py`

A linear workflow: `Coordinator` -> `Research` -> `Planner`.
Run it to see basic delegation:

```bash
python -m stages.stage3.demo --verbose
```

## 3. Activity: Red Team vs. Blue Team (File-Based)

File: `stages/stage3/activity/starter_workflow.py`

**The Players:**
1.  **Red Team (Attacker):** Reads `server.py`, identifies vulnerabilities, and reports them to the shared state.
2.  **Blue Team (Defender):** Reads `server.py` and the reported issues, then **rewrites the file** to fix them.
3.  **CISO (Judge):** Orchestrates the loop. They keep sending the Red Team back to check the Blue Team's work until the code is clean (or time runs out).

**Your Goal:**
1. **Implement the Red  and Blue Team workflow:** See  `stages/stage3/activity/starter_workflow.py` for the skeleton code.
2.  **Run the simulation:** `python -m stages.stage3.activity.starter_workflow`
3.  **Watch the battle:** Observe how the file `stages/stage3/activity/server.py` changes on disk.
4.  **Inspect the result:** Did the Blue Team fix everything? Did they break the code syntax?

**Stretch ideas**
- Add a `TestAgent` that tries to actually run the code (`python server.py`) and curls it to ensure the Blue Team didn't break functionality while fixing security.
- Give the Red Team a specific "Exploit Database" via MCP to find more obscure bugs.

Congrats! You've built a system that autonomously improves code quality.