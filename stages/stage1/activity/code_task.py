"""
Mini coding task for the Stage 1 activity.

Learners should implement the ``format_stage_report`` function using the
``write.file`` tool that they add to ``starter_agent.py``. Keep the task simple:

1. Accept a ``stage_name`` and a list of textual ``highlights``.
2. Return a multi-line string that looks like:

   Stage: Stage 1
   Highlights:
   - custom tools
   - write file helpers

3. Preserve the order of ``highlights`` and trim whitespace around each entry.
4. When ``highlights`` is empty, emit ``"- (none yet)"`` as the sole bullet.

Run ``python -m stages.stage1.activity.code_task`` after implementing the
function to confirm the output formatting.
"""

from __future__ import annotations

from typing import Iterable


def format_stage_report(stage_name: str, highlights: Iterable[str]) -> str:
    """
    Format a compact progress note for a workshop stage.

    Replace this placeholder implementation by calling the ``write.file`` tool
    from your agent. Return a string that follows the sample shown in the
    module docstring.
    """
    raise NotImplementedError(
        "Use the write.file tool to implement format_stage_report."
    )


if __name__ == "__main__":
    SAMPLE_OUTPUT = format_stage_report(
        "Stage 1",
        ["custom bash tool", "write tool", "workspace safety"],
    )
    print(SAMPLE_OUTPUT)
