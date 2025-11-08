# Stage 1 · Custom Bash Tool

Stage 0 confirmed the SDK wiring with a mock weather tool. Stage 1 levels up by letting the model run *real* shell commands via a bespoke `@function_tool` that enforces a tight allowlist.

## Learning Goals

- Wrap subprocess calls with `function_tool` and return structured `ToolOutputText`.
- Enforce guardrails (command allowlist, workspace path checks, timeouts, truncation).
- Guide an agent so it calls the tool deliberately and reports what it executed.

## 1. The `bash.run` Tool

Implementation: `utils/bash_tool.py`

- Accepts commands like `ls`, `pwd`, `cat`, `head`, `tail`, `stat`, `wc`, `find`, `grep`.
- Validates that every argument stays under `/workspace`.
- Uses `subprocess.run(..., timeout=5, capture_output=True)` so results are streamed back safely.
- Returns a `ToolOutputText` payload summarising stdout/stderr plus the exit code.

Feel free to extend the allowlist or the output formatting once you are comfortable with the basics.

## 2. Demo Walkthrough

File: `stages/stage1/demo.py`

- Imports `run_bash_command` and exposes it to the agent as the `bash.run` tool.
- Instructions remind the model to cite the commands it used.
- The prompt asks for: root directories, Dockerfile presence, and a suggested next command.

Run it:

```bash
python -m stages.stage1.demo --verbose
# append --verbose to stream the tool calls in real time
```

You should see the agent call `bash.run` a few times before composing the final answer.

## 3. Activity

Files:

- `stages/stage1/activity/starter_agent.py`
- `stages/stage1/activity/code_task.py`

Goal: build a "write-enabled" agent that can inspect the repository, add its
own `read.file`/`write.file` tools, and then use them to finish the coding task
inside `code_task.py`.

### What to Build

1. Implement a `read.file` function tool that:
   - Prints numbered lines (with optional `start_line`/`end_line` arguments).
   - Enforces the same workspace guardrails as `bash.run`.
2. Implement a `write.file` function tool that:
   - Writes UTF-8 text to files under `/workspace`.
   - Supports an `overwrite` mode (default) and an `append` mode.
   - Accepts optional `start_line`/`end_line` parameters to replace only a
     slice of the file.
   - Rejects attempts to escape the workspace or overwrite directories.
3. Guide the agent (via system/user instructions) to:
   - Read `code_task.py` with `bash.run`/`read.file` to understand the
     specification for `format_stage_report`.
   - Plan the change before writing.
   - Call `write.file` with the *entire* new file contents or use a precise
     line-range replacement to implement the function.
   - Optionally run `python -m stages.stage1.activity.code_task` to preview the
     behavior once implemented.
4. Summarize the work, citing any files or commands used.

The starter already wires `run_bash_command` into the agent. Update the system
instructions and user prompt so the agent focuses on finishing `code_task.py`.

Run your agent with:

```bash
python -m stages.stage1.activity.starter_agent --verbose
# append --verbose to stream the tool calls in real time
```

Once this stage feels comfortable, continue to Stage 2 to combine custom tools
with a FastMCP server.
