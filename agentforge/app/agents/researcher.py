"""AgentForge — Researcher Agent.

Specializes in gathering information using web search and URL reading tools.
"""

from __future__ import annotations

import json
import logging

import openai

from app.config import get_settings
from app.tools.search import SEARCH_TOOLS, TOOL_MAP

logger = logging.getLogger(__name__)

RESEARCHER_SYSTEM_PROMPT = """You are a Research Agent. Your specialty is gathering information.

You have access to:
- web_search: Search the web for information
- read_url: Read content from a specific URL

Guidelines:
- Be thorough in your research
- Use multiple search queries if needed
- Summarize findings clearly with sources
- Focus on factual, relevant information"""


class ResearcherAgent:
    """Agent that gathers information using search and URL tools."""

    def __init__(self):
        settings = get_settings()
        self.client = openai.OpenAI(api_key=settings.openai_api_key)
        self.model = settings.openai_model

    def execute(self, instructions: str, context: str = "") -> str:
        """Execute a research task.

        Args:
            instructions: What to research.
            context: Additional context from previous agents.

        Returns:
            Research findings as a string.
        """
        messages = [
            {"role": "system", "content": RESEARCHER_SYSTEM_PROMPT},
            {
                "role": "user",
                "content": f"Instructions: {instructions}\n\nContext: {context}",
            },
        ]

        # Initial call (may trigger tool use)
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            tools=SEARCH_TOOLS,
            temperature=0.1,
        )

        msg = response.choices[0].message

        # Handle tool calls
        max_tool_rounds = 3
        for _ in range(max_tool_rounds):
            if not msg.tool_calls:
                break

            messages.append(msg)

            for tool_call in msg.tool_calls:
                fn_name = tool_call.function.name
                fn_args = json.loads(tool_call.function.arguments)

                logger.info(f"Researcher calling tool: {fn_name}({fn_args})")

                if fn_name in TOOL_MAP:
                    result = TOOL_MAP[fn_name](**fn_args)
                else:
                    result = f"Unknown tool: {fn_name}"

                messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": str(result),
                    }
                )

            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                tools=SEARCH_TOOLS,
                temperature=0.1,
            )
            msg = response.choices[0].message

        result = msg.content or "No research findings."
        logger.info(f"Researcher completed: {len(result)} chars")
        return result
