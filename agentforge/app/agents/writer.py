"""AgentForge — Writer Agent.

Specializes in composing well-structured reports and content.
"""

from __future__ import annotations

import json
import logging

import openai

from app.config import get_settings
from app.tools.file_ops import FILE_TOOLS, TOOL_MAP

logger = logging.getLogger(__name__)

WRITER_SYSTEM_PROMPT = """You are a Writer Agent. Your specialty is composing clear, well-structured content.

You have access to:
- save_file: Save content to the workspace
- read_file: Read existing files
- list_files: List workspace files

Guidelines:
- Write clear, professional content
- Use proper structure with headings and sections
- Synthesize information from research and analysis
- Create actionable, reader-friendly outputs
- Save important outputs as files"""


class WriterAgent:
    """Agent that composes reports and structured content."""

    def __init__(self):
        settings = get_settings()
        self.client = openai.OpenAI(api_key=settings.openai_api_key)
        self.model = settings.openai_model

    def execute(self, instructions: str, context: str = "") -> str:
        """Execute a writing task.

        Args:
            instructions: What to write.
            context: Research/analysis from previous agents.

        Returns:
            Written content as a string.
        """
        messages = [
            {"role": "system", "content": WRITER_SYSTEM_PROMPT},
            {
                "role": "user",
                "content": f"Instructions: {instructions}\n\nInput Data:\n{context}",
            },
        ]

        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            tools=FILE_TOOLS,
            temperature=0.3,
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

                logger.info(f"Writer calling tool: {fn_name}")

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
                tools=FILE_TOOLS,
                temperature=0.3,
            )
            msg = response.choices[0].message

        result = msg.content or "No content generated."
        logger.info(f"Writer completed: {len(result)} chars")
        return result
