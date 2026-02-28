"""AgentForge — Shared State Schema for LangGraph."""

from __future__ import annotations

from typing import Annotated, Sequence
from dataclasses import dataclass, field

from typing_extensions import TypedDict


def add_messages(existing: list[dict], new: list[dict]) -> list[dict]:
    """Reducer that appends new messages to existing ones."""
    return existing + new


class AgentState(TypedDict):
    """Shared state passed between all agents in the workflow.

    Attributes:
        task: The original user task/query.
        messages: Conversation history (accumulated via reducer).
        current_agent: Which agent is currently active.
        research_data: Data gathered by the researcher agent.
        analysis_results: Results from the analyst agent.
        final_output: The final composed output.
        iteration_count: Number of workflow iterations.
        status: Current workflow status.
    """

    task: str
    messages: Annotated[list[dict], add_messages]
    current_agent: str
    research_data: list[str]
    analysis_results: list[str]
    final_output: str
    iteration_count: int
    status: str


def create_initial_state(task: str) -> AgentState:
    """Create the initial state for a workflow run."""
    return AgentState(
        task=task,
        messages=[],
        current_agent="supervisor",
        research_data=[],
        analysis_results=[],
        final_output="",
        iteration_count=0,
        status="started",
    )
