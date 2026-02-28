"""AgentForge — Calculator Tool."""

from __future__ import annotations

import json
import math
import logging
import statistics
from typing import Any

logger = logging.getLogger(__name__)


def calculate(expression: str) -> str:
    """Evaluate a mathematical expression safely.

    Args:
        expression: Mathematical expression to evaluate.

    Returns:
        Result as a string.
    """
    logger.info(f"Calculating: {expression}")

    # Safe eval with only math functions
    allowed_names = {
        k: v
        for k, v in math.__dict__.items()
        if not k.startswith("_")
    }
    allowed_names.update({
        "abs": abs,
        "round": round,
        "min": min,
        "max": max,
        "sum": sum,
        "len": len,
    })

    try:
        result = eval(expression, {"__builtins__": {}}, allowed_names)
        return str(result)
    except Exception as e:
        return f"Error evaluating expression: {e}"


def compute_statistics(data: list[float]) -> str:
    """Compute descriptive statistics for a dataset.

    Args:
        data: List of numerical values.

    Returns:
        JSON string of computed statistics.
    """
    if not data:
        return json.dumps({"error": "Empty dataset"})

    stats = {
        "count": len(data),
        "mean": statistics.mean(data),
        "median": statistics.median(data),
        "std_dev": statistics.stdev(data) if len(data) > 1 else 0,
        "min": min(data),
        "max": max(data),
        "sum": sum(data),
    }

    logger.info(f"Computed statistics for {len(data)} values")
    return json.dumps(stats, indent=2)


CALCULATOR_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "calculate",
            "description": "Evaluate a mathematical expression. Supports standard math operations and functions.",
            "parameters": {
                "type": "object",
                "properties": {
                    "expression": {
                        "type": "string",
                        "description": "Math expression, e.g. '2 * 3 + sqrt(16)'",
                    },
                },
                "required": ["expression"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "compute_statistics",
            "description": "Compute descriptive statistics (mean, median, std dev, etc.) for a list of numbers.",
            "parameters": {
                "type": "object",
                "properties": {
                    "data": {
                        "type": "array",
                        "items": {"type": "number"},
                        "description": "List of numerical values",
                    },
                },
                "required": ["data"],
            },
        },
    },
]

TOOL_MAP = {
    "calculate": calculate,
    "compute_statistics": compute_statistics,
}
