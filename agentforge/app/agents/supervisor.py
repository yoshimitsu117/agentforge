"""AgentForge — Supervisor Agent.

The supervisor agent acts as a router/planner, deciding which
specialized agent should handle each step of the workflow.
"""

from __future__ import annotations

import json
import logging

import openai

from app.config import get_settings

logger = logging.getLogger(__name__)

SUPERVISOR_SYSTEM_PROMPT = """You are a Supervisor agent managing a team of specialized AI agents.
Your team consists of:
1. **Researcher** — Gathers information via web search and URL reading
2. **Analyst** — Performs calculations, data analysis, and statistical computations
3. **Writer** — Composes well-structured reports, summaries, and content

Your job is to:
1. Analyze the user's task
2. Break it into subtasks
3. Route each subtask to the appropriate agent
4. Decide when the task is complete

Respond with a JSON object:
{
    "next_agent": "researcher" | "analyst" | "writer" | "FINISH",
    "instructions": "Specific instructions for the next agent",
    "reasoning": "Why you chose this agent"
}

If the task is complete and all agents have done their part, set next_agent to "FINISH"."""


class SupervisorAgent:
    """Routes tasks to specialized agents based on the current state."""

    def __init__(self):
        settings = get_settings()
        self.client = openai.OpenAI(api_key=settings.openai_api_key)
        self.model = settings.openai_model

    def decide(self, state: dict) -> dict:
        """Determine which agent should act next.

        Args:
            state: Current workflow state.

        Returns:
            Decision dict with next_agent, instructions, reasoning.
        """
        messages = [
            {"role": "system", "content": SUPERVISOR_SYSTEM_PROMPT},
            {
                "role": "user",
                "content": self._build_context(state),
            },
        ]

        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=0.1,
            response_format={"type": "json_object"},
        )

        content = response.choices[0].message.content or "{}"

        try:
            decision = json.loads(content)
        except json.JSONDecodeError:
            decision = {
                "next_agent": "FINISH",
                "instructions": "Could not parse decision",
                "reasoning": "JSON parse error",
            }

        logger.info(
            f"Supervisor decision: {decision.get('next_agent')} — "
            f"{decision.get('reasoning', '')[:80]}"
        )
        return decision

    def _build_context(self, state: dict) -> str:
        """Build context string from current state."""
        parts = [f"**Original Task:** {state.get('task', 'No task')}"]

        if state.get("research_data"):
            parts.append(
                f"\n**Research gathered so far:**\n"
                + "\n".join(f"- {d[:200]}" for d in state["research_data"][-3:])
            )

        if state.get("analysis_results"):
            parts.append(
                f"\n**Analysis results:**\n"
                + "\n".join(f"- {r[:200]}" for r in state["analysis_results"][-3:])
            )

        if state.get("final_output"):
            parts.append(f"\n**Draft output exists:** Yes ({len(state['final_output'])} chars)")

        parts.append(f"\n**Iteration:** {state.get('iteration_count', 0)}")

        # Include recent messages
        recent = state.get("messages", [])[-5:]
        if recent:
            parts.append("\n**Recent conversation:**")
            for msg in recent:
                role = msg.get("role", "unknown")
                content = msg.get("content", "")[:150]
                parts.append(f"  [{role}]: {content}")

        return "\n".join(parts)
