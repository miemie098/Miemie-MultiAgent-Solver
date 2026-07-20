"""
API endpoint tests — verify the FastAPI server responds correctly.
"""
import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def client():
    """Create a TestClient for the FastAPI app."""
    from app.main import app
    return TestClient(app)


class TestHealthEndpoint:
    """Tests for GET /api/health"""

    def test_health_returns_ok(self, client):
        response = client.get("/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["workflow_compiled"] is True


class TestFrontend:
    """Tests for GET /"""

    def test_frontend_served(self, client):
        response = client.get("/")
        assert response.status_code == 200
        assert "text/html" in response.headers.get("content-type", "")


class TestSolveEndpoint:
    """Tests for POST /api/solve"""

    def test_solve_validates_query_required(self, client):
        """SolverRequest requires a query field."""
        response = client.post("/api/solve", json={})
        assert response.status_code == 422  # Pydantic validation error

    def test_solve_validates_max_corrections_range(self, client):
        """max_corrections must be >= 1 and <= 10."""
        response = client.post("/api/solve", json={
            "query": "test",
            "max_corrections": 0,
        })
        assert response.status_code == 422

        response = client.post("/api/solve", json={
            "query": "test",
            "max_corrections": 11,
        })
        assert response.status_code == 422
