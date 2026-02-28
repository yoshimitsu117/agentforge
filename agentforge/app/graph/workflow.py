"""AgentForge — LangGraph Workflow Definition."""

from __future__ import annotations

import logging

from langgraph.graph import StateGraph, END

from app.config import get_settings
from app.graph.state import AgentState, create_initial_state
from app.graph.nodes import (
    supervisor_node,
    researcher_node,
    analyst_node,
    writer_node,
)

logger = logging.getLogger(__name__)


def route_agent(state: AgentState) -> str:
    """Route to the next agent based on supervisor's decision."""
    next_agent = state.get("current_agent", "FINISH")
    settings = get_settings()

    # Safety: stop after max iterations
    if state.get("iteration_count", 0) >= settings.max_iterations:
        logger.warning("Max iterations reached — finishing workflow")
        return "finish"

    routing = {
        "researcher": "researcher",
        "analyst": "analyst",
        "writer": "writer",
        "FINISH": "finish",
    }

    return routing.get(next_agent, "finish")


def build_workflow() -> StateGraph:
    """Build the multi-agent LangGraph workflow.

    Graph structure:
        supervisor → (researcher | analyst | writer | FINISH)
        researcher → supervisor
        analyst → supervisor
        writer → supervisor

    Returns:
        Compiled StateGraph ready for execution.
    """
    workflow = StateGraph(AgentState)

    # Add nodes
    workflow.add_node("supervisor", supervisor_node)
    workflow.add_node("researcher", researcher_node)
    workflow.add_node("analyst", analyst_node)
    workflow.add_node("writer", writer_node)

    # Set entry point
    workflow.set_entry_point("supervisor")

    # Conditional routing from supervisor
    workflow.add_conditional_edges(
        "supervisor",
        route_agent,
        {
            "researcher": "researcher",
            "analyst": "analyst",
            "writer": "writer",
            "finish": END,
        },
    )

    # All agents route back to supervisor
    workflow.add_edge("researcher", "supervisor")
    workflow.add_edge("analyst", "supervisor")
    workflow.add_edge("writer", "supervisor")

    return workflow


def create_app():
    """Create and compile the workflow application."""
    workflow = build_workflow()
    app = workflow.compile()
    logger.info("AgentForge workflow compiled successfully")
    return app


def run_workflow(task: str) -> dict:
    """Run a complete workflow for a given task.

    Args:
        task: The user's task description.

    Returns:
        Final state dict with all results.
    """
    app = create_app()
    initial_state = create_initial_state(task)

    logger.info(f"Starting workflow: '{task[:80]}...'")
    final_state = app.invoke(initial_state)

    logger.info(
        f"Workflow complete: {final_state.get('iteration_count', 0)} iterations"
    )
    return dict(final_state)
