"""AgentForge — LangGraph Node Definitions."""

from __future__ import annotations

import logging

from app.agents.supervisor import SupervisorAgent
from app.agents.researcher import ResearcherAgent
from app.agents.analyst import AnalystAgent
from app.agents.writer import WriterAgent
from app.graph.state import AgentState

logger = logging.getLogger(__name__)

# Lazy-initialized agents
_supervisor: SupervisorAgent | None = None
_researcher: ResearcherAgent | None = None
_analyst: AnalystAgent | None = None
_writer: WriterAgent | None = None


def _get_supervisor() -> SupervisorAgent:
    global _supervisor
    if _supervisor is None:
        _supervisor = SupervisorAgent()
    return _supervisor


def _get_researcher() -> ResearcherAgent:
    global _researcher
    if _researcher is None:
        _researcher = ResearcherAgent()
    return _researcher


def _get_analyst() -> AnalystAgent:
    global _analyst
    if _analyst is None:
        _analyst = AnalystAgent()
    return _analyst


def _get_writer() -> WriterAgent:
    global _writer
    if _writer is None:
        _writer = WriterAgent()
    return _writer


def supervisor_node(state: AgentState) -> dict:
    """Supervisor decides which agent should work next."""
    supervisor = _get_supervisor()
    decision = supervisor.decide(dict(state))

    return {
        "current_agent": decision.get("next_agent", "FINISH"),
        "messages": [
            {
                "role": "supervisor",
                "content": f"Routing to {decision.get('next_agent')}: "
                f"{decision.get('instructions', '')}",
            }
        ],
        "iteration_count": state["iteration_count"] + 1,
    }


def researcher_node(state: AgentState) -> dict:
    """Researcher gathers information using search tools."""
    researcher = _get_researcher()

    # Get latest supervisor instructions
    instructions = ""
    for msg in reversed(state.get("messages", [])):
        if msg.get("role") == "supervisor":
            instructions = msg.get("content", "")
            break

    context = "\n".join(state.get("research_data", [])[-3:])
    result = researcher.execute(instructions=instructions, context=context)

    return {
        "research_data": [result],
        "messages": [
            {"role": "researcher", "content": f"Research complete: {result[:200]}..."}
        ],
        "current_agent": "supervisor",
    }


def analyst_node(state: AgentState) -> dict:
    """Analyst performs calculations and data analysis."""
    analyst = _get_analyst()

    instructions = ""
    for msg in reversed(state.get("messages", [])):
        if msg.get("role") == "supervisor":
            instructions = msg.get("content", "")
            break

    context = "\n".join(
        state.get("research_data", [])[-3:]
        + state.get("analysis_results", [])[-3:]
    )
    result = analyst.execute(instructions=instructions, context=context)

    return {
        "analysis_results": [result],
        "messages": [
            {"role": "analyst", "content": f"Analysis complete: {result[:200]}..."}
        ],
        "current_agent": "supervisor",
    }


def writer_node(state: AgentState) -> dict:
    """Writer composes the final output."""
    writer = _get_writer()

    instructions = ""
    for msg in reversed(state.get("messages", [])):
        if msg.get("role") == "supervisor":
            instructions = msg.get("content", "")
            break

    context_parts = []
    if state.get("research_data"):
        context_parts.append("## Research\n" + "\n".join(state["research_data"]))
    if state.get("analysis_results"):
        context_parts.append("## Analysis\n" + "\n".join(state["analysis_results"]))

    context = "\n\n".join(context_parts)
    result = writer.execute(instructions=instructions, context=context)

    return {
        "final_output": result,
        "messages": [
            {"role": "writer", "content": f"Writing complete: {result[:200]}..."}
        ],
        "current_agent": "supervisor",
    }
