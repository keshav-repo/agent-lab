import json
import re
from pathlib import Path

from sqlLiteDB import init_db
from vectorDb import init_chroma

PROJECT_DIR = Path(__file__).resolve().parent
CONFIG_PATH = PROJECT_DIR / "workspace" / "workspaces.json"
WORKSPACES_ROOT = PROJECT_DIR / "workspaces"

DEFAULT_CONFIG = {
    "active_workspace": "Default",
    "workspaces": [
        {
            "name": "Default",
            "path": "workspaces/default",
        }
    ],
}


def _slug(name: str) -> str:
    slug = re.sub(r"[^A-Za-z0-9_-]+", "_", name.strip()).strip("_")
    return slug.lower() or "workspace"


def _load() -> dict:
    if not CONFIG_PATH.exists():
        CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
        _save(DEFAULT_CONFIG)
        return json.loads(json.dumps(DEFAULT_CONFIG))

    with CONFIG_PATH.open("r", encoding="utf-8") as file:
        data = json.load(file)

    workspaces = data.get("workspaces") or []
    if not workspaces:
        data = json.loads(json.dumps(DEFAULT_CONFIG))
        _save(data)
    return data


def _save(data: dict) -> None:
    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with CONFIG_PATH.open("w", encoding="utf-8") as file:
        json.dump(data, file, indent=2)
        file.write("\n")


def _resolve_path(path_str: str) -> Path:
    path = Path(path_str)
    if not path.is_absolute():
        return (PROJECT_DIR / path).resolve()
    return path


def _find_workspace(data: dict, name: str) -> dict | None:
    target = name.strip().lower()
    for workspace in data.get("workspaces", []):
        workspace_name = str(workspace.get("name", "")).lower()
        path_name = Path(workspace.get("path", "")).name.lower()
        if workspace_name == target or path_name == target:
            return workspace
    return None


def _activate(workspace: dict) -> Path:
    workspace_dir = _resolve_path(workspace["path"])
    workspace_dir.mkdir(parents=True, exist_ok=True)
    init_db(workspace_dir)
    init_chroma(workspace_dir)
    return workspace_dir


def get_workspaces() -> list[dict]:
    return list(_load().get("workspaces", []))


def get_active_workspace() -> dict:
    data = _load()
    active_name = str(data.get("active_workspace", ""))
    workspace = _find_workspace(data, active_name)
    if workspace is None:
        workspace = data["workspaces"][0]
    return dict(workspace)


def add_workspace(name: str) -> dict:
    name = (name or "").strip()
    if not name:
        raise ValueError("Workspace name is required")

    data = _load()
    if _find_workspace(data, name) is not None:
        raise ValueError(f"Workspace '{name}' already exists")

    slug = _slug(name)
    relative_path = f"workspaces/{slug}"
    if any(ws.get("path") == relative_path for ws in data["workspaces"]):
        raise ValueError(f"Workspace path '{relative_path}' already exists")

    workspace_dir = WORKSPACES_ROOT / slug
    workspace_dir.mkdir(parents=True, exist_ok=True)

    workspace = {"name": name, "path": relative_path}
    data["workspaces"].append(workspace)
    _save(data)
    return workspace


def set_active_workspace(name: str) -> dict:
    name = (name or "").strip()
    if not name:
        raise ValueError("Workspace name is required")

    data = _load()
    workspace = _find_workspace(data, name)
    if workspace is None:
        raise ValueError(f"Workspace '{name}' was not found")

    data["active_workspace"] = workspace["name"]
    _save(data)
    _activate(workspace)
    return dict(workspace)


def bootstrap() -> dict:
    workspace = get_active_workspace()
    _activate(workspace)
    return workspace

