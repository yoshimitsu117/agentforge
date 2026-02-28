"""AgentForge — File Operations Tool."""

from __future__ import annotations

import json
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

WORKSPACE_DIR = Path("./workspace")


def save_file(filename: str, content: str) -> str:
    """Save content to a file in the workspace.

    Args:
        filename: Name of the file to save.
        content: Content to write.

    Returns:
        Confirmation message.
    """
    WORKSPACE_DIR.mkdir(parents=True, exist_ok=True)
    path = WORKSPACE_DIR / filename
    path.write_text(content, encoding="utf-8")
    logger.info(f"Saved file: {path}")
    return f"File saved: {filename} ({len(content)} characters)"


def read_file(filename: str) -> str:
    """Read content from a file in the workspace.

    Args:
        filename: Name of the file to read.

    Returns:
        File content or error message.
    """
    path = WORKSPACE_DIR / filename
    if not path.exists():
        return f"Error: File '{filename}' not found in workspace."
    content = path.read_text(encoding="utf-8")
    logger.info(f"Read file: {path} ({len(content)} chars)")
    return content


def list_files() -> str:
    """List all files in the workspace.

    Returns:
        JSON list of files.
    """
    WORKSPACE_DIR.mkdir(parents=True, exist_ok=True)
    files = [
        {"name": f.name, "size": f.stat().st_size}
        for f in WORKSPACE_DIR.iterdir()
        if f.is_file()
    ]
    return json.dumps(files, indent=2)


FILE_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "save_file",
            "description": "Save content to a file in the workspace directory.",
            "parameters": {
                "type": "object",
                "properties": {
                    "filename": {"type": "string", "description": "File name"},
                    "content": {"type": "string", "description": "Content to save"},
                },
                "required": ["filename", "content"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "Read content from a file in the workspace.",
            "parameters": {
                "type": "object",
                "properties": {
                    "filename": {"type": "string", "description": "File name to read"},
                },
                "required": ["filename"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "list_files",
            "description": "List all files in the workspace directory.",
            "parameters": {
                "type": "object",
                "properties": {},
            },
        },
    },
]

TOOL_MAP = {
    "save_file": save_file,
    "read_file": read_file,
    "list_files": list_files,
}
