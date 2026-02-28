"""AgentForge — FastAPI Application.

Multi-Agent AI Workflow Engine powered by LangGraph.
"""

from __future__ import annotations

import logging
import uuid
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from app.config import get_settings
from app.graph.workflow import run_workflow
from app.memory.store import memory

logger = logging.getLogger(__name__)

# Store workflow results
_workflow_results: dict[str, dict] = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    logging.basicConfig(
        level=getattr(logging, settings.log_level),
        format="%(asctime)s | %(name)s | %(levelname)s | %(message)s",
    )
    logger.info(f"Starting {settings.app_name} v{settings.app_version}")
    yield
    logger.info("Shutting down AgentForge")


app = FastAPI(
    title="AgentForge API",
    description="Multi-Agent AI Workflow Engine",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ------------------------------------------------------------------
# Schemas
# ------------------------------------------------------------------
class WorkflowRequest(BaseModel):
    task: str = Field(..., description="Task for the agent workflow")
    config: dict = Field(default_factory=dict, description="Optional config overrides")


class WorkflowResponse(BaseModel):
    workflow_id: str
    status: str
    task: str
    final_output: str
    iterations: int
    research_data: list[str]
    analysis_results: list[str]


class AgentInfo(BaseModel):
    name: str
    description: str
    tools: list[str]


# ------------------------------------------------------------------
# Routes
# ------------------------------------------------------------------
@app.get("/health")
async def health_check():
    settings = get_settings()
    return {
        "status": "healthy",
        "app": settings.app_name,
        "version": settings.app_version,
        "active_sessions": len(memory.list_sessions()),
    }


@app.post("/api/v1/workflow", response_model=WorkflowResponse)
async def execute_workflow(request: WorkflowRequest):
    """Execute a multi-agent workflow."""
    workflow_id = str(uuid.uuid4())[:8]

    try:
        # Run the workflow
        final_state = run_workflow(request.task)

        # Store result
        _workflow_results[workflow_id] = final_state

        # Save to memory
        memory.add_message(
            session_id=workflow_id,
            role="user",
            content=request.task,
        )
        memory.add_message(
            session_id=workflow_id,
            role="system",
            content=final_state.get("final_output", ""),
        )

        return WorkflowResponse(
            workflow_id=workflow_id,
            status="completed",
            task=request.task,
            final_output=final_state.get("final_output", "No output generated"),
            iterations=final_state.get("iteration_count", 0),
            research_data=final_state.get("research_data", []),
            analysis_results=final_state.get("analysis_results", []),
        )

    except Exception as e:
        logger.error(f"Workflow failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/workflow/{workflow_id}")
async def get_workflow_result(workflow_id: str):
    """Get the result of a previously executed workflow."""
    result = _workflow_results.get(workflow_id)
    if not result:
        raise HTTPException(status_code=404, detail="Workflow not found")

    return {
        "workflow_id": workflow_id,
        "status": "completed",
        "final_output": result.get("final_output", ""),
        "iterations": result.get("iteration_count", 0),
    }


@app.get("/api/v1/agents", response_model=list[AgentInfo])
async def list_agents():
    """List all available agents and their capabilities."""
    return [
        AgentInfo(
            name="Supervisor",
            description="Routes tasks to specialized agents",
            tools=["routing", "planning"],
        ),
        AgentInfo(
            name="Researcher",
            description="Gathers information via web search",
            tools=["web_search", "read_url"],
        ),
        AgentInfo(
            name="Analyst",
            description="Performs data analysis and calculations",
            tools=["calculate", "compute_statistics"],
        ),
        AgentInfo(
            name="Writer",
            description="Composes reports and structured content",
            tools=["save_file", "read_file", "list_files"],
        ),
    ]
