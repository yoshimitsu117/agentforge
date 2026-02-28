"""Tests for AgentForge workflow engine."""

import pytest

from app.graph.state import AgentState, create_initial_state
from app.memory.store import MemoryStore
from app.tools.calculator import calculate, compute_statistics
from app.tools.search import web_search
from app.tools.file_ops import save_file, read_file, list_files


class TestState:
    """Tests for the workflow state."""

    def test_create_initial_state(self):
        state = create_initial_state("Test task")
        assert state["task"] == "Test task"
        assert state["messages"] == []
        assert state["current_agent"] == "supervisor"
        assert state["iteration_count"] == 0
        assert state["status"] == "started"

    def test_state_has_all_fields(self):
        state = create_initial_state("task")
        expected_keys = {
            "task", "messages", "current_agent", "research_data",
            "analysis_results", "final_output", "iteration_count", "status",
        }
        assert set(state.keys()) == expected_keys


class TestMemoryStore:
    """Tests for conversation memory."""

    def test_add_and_get_message(self):
        store = MemoryStore()
        store.add_message("sess1", "user", "Hello")
        history = store.get_history("sess1")
        assert len(history) == 1
        assert history[0]["role"] == "user"
        assert history[0]["content"] == "Hello"

    def test_multiple_sessions(self):
        store = MemoryStore()
        store.add_message("sess1", "user", "Hello 1")
        store.add_message("sess2", "user", "Hello 2")
        assert len(store.get_history("sess1")) == 1
        assert len(store.get_history("sess2")) == 1

    def test_get_last_n(self):
        store = MemoryStore()
        for i in range(10):
            store.add_message("sess1", "user", f"Message {i}")
        history = store.get_history("sess1", last_n=3)
        assert len(history) == 3
        assert history[0]["content"] == "Message 7"

    def test_clear_session(self):
        store = MemoryStore()
        store.add_message("sess1", "user", "Hi")
        store.clear_session("sess1")
        assert len(store.get_history("sess1")) == 0

    def test_list_sessions(self):
        store = MemoryStore()
        store.add_message("a", "user", "1")
        store.add_message("b", "user", "2")
        sessions = store.list_sessions()
        assert set(sessions) == {"a", "b"}

    def test_context_string(self):
        store = MemoryStore()
        store.add_message("s", "user", "Hello")
        store.add_message("s", "assistant", "Hi there")
        ctx = store.get_context_string("s")
        assert "[user]: Hello" in ctx
        assert "[assistant]: Hi there" in ctx


class TestCalculatorTools:
    """Tests for calculator tools."""

    def test_basic_calculation(self):
        result = calculate("2 + 3")
        assert result == "5"

    def test_math_functions(self):
        result = calculate("sqrt(16)")
        assert result == "4.0"

    def test_invalid_expression(self):
        result = calculate("invalid_func()")
        assert "Error" in result

    def test_compute_statistics(self):
        import json
        result = json.loads(compute_statistics([1, 2, 3, 4, 5]))
        assert result["count"] == 5
        assert result["mean"] == 3.0
        assert result["min"] == 1
        assert result["max"] == 5

    def test_empty_statistics(self):
        import json
        result = json.loads(compute_statistics([]))
        assert "error" in result


class TestSearchTools:
    """Tests for search tools."""

    def test_web_search_returns_results(self):
        import json
        results = json.loads(web_search("test query", num_results=3))
        assert len(results) == 3
        assert all("title" in r for r in results)
        assert all("url" in r for r in results)
        assert all("snippet" in r for r in results)


class TestFileOpsTools:
    """Tests for file operation tools."""

    def test_save_and_read_file(self, tmp_path, monkeypatch):
        import app.tools.file_ops as fops
        monkeypatch.setattr(fops, "WORKSPACE_DIR", tmp_path)

        save_result = save_file("test.txt", "Hello World")
        assert "saved" in save_result.lower()

        content = read_file("test.txt")
        assert content == "Hello World"

    def test_read_nonexistent_file(self, tmp_path, monkeypatch):
        import app.tools.file_ops as fops
        monkeypatch.setattr(fops, "WORKSPACE_DIR", tmp_path)

        result = read_file("nope.txt")
        assert "not found" in result.lower()

    def test_list_files(self, tmp_path, monkeypatch):
        import json
        import app.tools.file_ops as fops
        monkeypatch.setattr(fops, "WORKSPACE_DIR", tmp_path)

        (tmp_path / "a.txt").write_text("aaa")
        (tmp_path / "b.txt").write_text("bbb")

        result = json.loads(list_files())
        names = {f["name"] for f in result}
        assert "a.txt" in names
        assert "b.txt" in names
