🤖 AgentForge

**Multi-Agent AI Workflow Engine powered by LangGraph**

![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![LangGraph](https://img.shields.io/badge/LangGraph-Agents-1C3C3C?style=for-the-badge)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)

---

## 🧠 Overview

AgentForge is a **multi-agent orchestration framework** that uses LangGraph to coordinate specialized AI agents for complex task workflows. It features a **supervisor agent** that dynamically routes tasks to domain-specific agents (researcher, analyst, writer), each equipped with dedicated tools.

Built for **production use** — with state persistence, streaming execution, human-in-the-loop support, and a REST API for integration.

---

## 🏗️ Architecture

```
                    ┌───────────────────┐
                    │   FastAPI Server   │
                    │  /api/v1/workflow  │
                    └─────────┬─────────┘
                              │
                    ┌─────────▼─────────┐
                    │   Supervisor Agent │
                    │   (Router/Planner) │
                    └────┬────┬────┬────┘
                         │    │    │
              ┌──────────┘    │    └──────────┐
              │               │               │
    ┌─────────▼──────┐ ┌─────▼───────┐ ┌─────▼──────────┐
    │  Researcher    │ │  Analyst    │ │   Writer       │
    │  Agent         │ │  Agent      │ │   Agent        │
    │                │ │             │ │                │
    │ • Web Search   │ │ • Calculator │ │ • Formatting  │
    │ • URL Reader   │ │ • Data Parse │ │ • Summarize   │
    │ • Summarize    │ │ • Statistics │ │ • Structure   │
    └────────────────┘ └─────────────┘ └────────────────┘
              │               │               │
              └───────────────┼───────────────┘
                              │
                    ┌─────────▼─────────┐
                    │  Shared State     │
                    │  (Conversation    │
                    │   Memory + Context)│
                    └───────────────────┘
```

---

## ✨ Features

- **Multi-Agent Orchestration** — Supervisor dynamically routes to specialized agents
- **LangGraph Workflows** — Graph-based state machine for reliable execution
- **Tool Calling** — Each agent has dedicated tools (search, calculator, file ops)
- **Shared State** — Agents share context through typed state schema
- **Conversation Memory** — Persistent memory across workflow runs
- **Streaming Execution** — Real-time updates as agents work
- **Human-in-the-Loop** — Configurable checkpoints for human review
- **REST API** — FastAPI endpoints for workflow execution and management

---

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- OpenAI API key

### 1. Clone & Install
```bash
git clone https://github.com/yoshimitsu117/agentforge.git
cd agentforge
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Configure
```bash
cp .env.example .env
# Add your API keys
```

### 3. Run
```bash
uvicorn app.main:app --reload --port 8001
```

### 4. Execute a Workflow
```bash
curl -X POST http://localhost:8001/api/v1/workflow \
  -H "Content-Type: application/json" \
  -d '{
    "task": "Research the latest trends in AI agents and write a summary report",
    "config": {"max_iterations": 10}
  }'
```

---

## 🐳 Docker
```bash
docker-compose up --build
```

---

## 📡 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/v1/workflow` | Execute a multi-agent workflow |
| `POST` | `/api/v1/workflow/stream` | Stream workflow execution updates |
| `GET`  | `/api/v1/workflow/{id}` | Get workflow status/result |
| `GET`  | `/api/v1/agents` | List available agents |
| `GET`  | `/health` | Health check |

---

## 📁 Project Structure

```
agentforge/
├── app/
│   ├── main.py              # FastAPI server
│   ├── config.py             # Configuration
│   ├── agents/
│   │   ├── researcher.py    # Research agent with web search
│   │   ├── analyst.py       # Data analysis agent
│   │   ├── writer.py        # Content writer agent
│   │   └── supervisor.py    # Supervisor/router agent
│   ├── graph/
│   │   ├── workflow.py      # LangGraph workflow definition
│   │   ├── state.py         # Shared state schema
│   │   └── nodes.py         # Graph node definitions
│   ├── tools/
│   │   ├── search.py        # Web search tool
│   │   ├── calculator.py    # Math/calculation tool
│   │   └── file_ops.py      # File operations tool
│   └── memory/
│       └── store.py         # Conversation memory
├── tests/
│   └── test_workflow.py
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── .env.example
```

---

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.

---

## 👤 Author

**Siddharth** — AI Engineer  
Building production-grade AI systems, not just demos.

[![LinkedIn](https://img.shields.io/badge/LinkedIn-Connect-0077B5?style=flat&logo=linkedin)](https://linkedin.com/in/yoshimitsu117)
[![GitHub](https://img.shields.io/badge/GitHub-Follow-181717?style=flat&logo=github)](https://github.com/yoshimitsu117)
ADME.md…]()
