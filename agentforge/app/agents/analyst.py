"""AgentForge — Analyst Agent.

Specializes in data analysis, calculations, and statistical computations.
"""

from __future__ import annotations

import json
import logging

import openai

from app.config import get_settings
from app.tools.calculator import CALCULATOR_TOOLS, TOOL_MAP

logger = logging.getLogger(__name__)

ANALYST_SYSTEM_PROMPT = """You are an Analyst Agent. Your specialty is data analysis and computation.

You have access to:
- calculate: Evaluate mathematical expressions
- compute_statistics: Compute descriptive statistics for datasets

Guidelines:
- Perform accurate calculations
- Present data clearly with context  
- Identify patterns, trends, and insights
- Support conclusions with numbers"""


class AnalystAgent:
    """Agent that performs data analysis and computations."""

    def __init__(self):
        settings = get_settings()
        self.client = openai.OpenAI(api_key=settings.openai_api_key)
        self.model = settings.openai_model

    def execute(self, instructions: str, context: str = "") -> str:
        """Execute an analysis task.

        Args:
            instructions: What to analyze.
            context: Data or context from previous agents.

        Returns:
            Analysis results as a string.
        """
        messages = [
            {"role": "system", "content": ANALYST_SYSTEM_PROMPT},
            {
                "role": "user",
                "content": f"Instructions: {instructions}\n\nContext/Data: {context}",
            },
        ]

        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            tools=CALCULATOR_TOOLS,
            temperature=0.1,
        )

        msg = response.choices[0].message

        max_tool_rounds = 3
        for _ in range(max_tool_rounds):
            if not msg.tool_calls:
                break

            messages.append(msg)

            for tool_call in msg.tool_calls:
                fn_name = tool_call.function.name
                fn_args = json.loads(tool_call.function.arguments)

                logger.info(f"Analyst calling tool: {fn_name}({fn_args})")

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
                tools=CALCULATOR_TOOLS,
                temperature=0.1,
            )
            msg = response.choices[0].message

        result = msg.content or "No analysis results."
        logger.info(f"Analyst completed: {len(result)} chars")
        return result
