from pathlib import Path

WORKSPACE_ROOT = Path(__file__).resolve().parent.parent

def resolve_workspace_path(path: str, *, ensure_parent: bool = True) -> Path:
    candidate = Path(path)
    if not candidate.is_absolute():
        candidate = WORKSPACE_ROOT / path
    resolved = candidate.resolve()
    if not str(resolved).startswith(str(WORKSPACE_ROOT)):
        msg = f"Path escape blocked for '{path}'. Stay inside {WORKSPACE_ROOT}."
        raise ValueError(msg)
    if resolved.is_dir():
        msg = f"'{path}' is a directory. write.file targets files only."
        raise ValueError(msg)
    if ensure_parent:
        resolved.parent.mkdir(parents=True, exist_ok=True)
    return resolved


__all__ = ["WORKSPACE_ROOT", "resolve_workspace_path"]