"""Functional tests for FastAPI web endpoints and status APIs."""

import unittest

from starlette.testclient import TestClient

from src.web.app import create_app


class TestWebApiEndpoints(unittest.TestCase):
    """Scenario: Verify HTTP API endpoints and response structure."""

    def setUp(self) -> None:
        """Create test client for FastAPI application instance."""
        self.app = create_app()
        self.client = TestClient(self.app)

    def test_should_return_dashboard_status(self) -> None:
        """Test /api/status returns JSON with required telemetry keys."""
        response = self.client.get("/api/status")
        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertIn("is_authorized", data)
        self.assertIn("auth_status", data)
        self.assertIn("total_chats", data)
        self.assertIn("total_messages", data)
        self.assertIn("infographics_count", data)
        self.assertIn("task_running", data)

    def test_should_list_infographics_grouped_by_categories(self) -> None:
        """Test /api/infographics returns categorised visualization schema."""
        response = self.client.get("/api/infographics")
        self.assertEqual(response.status_code, 200)

        categories = response.json()
        self.assertIn("dashboard", categories)
        self.assertIn("time", categories)
        self.assertIn("style", categories)
        self.assertIn("social", categories)

    def test_should_return_report_payload(self) -> None:
        """Test /api/report returns valid status dictionary."""
        response = self.client.get("/api/report")
        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertIn("exists", data)

    def test_should_handle_logout_endpoint(self) -> None:
        """Test /api/auth/logout clears user authentication."""
        response = self.client.post("/api/auth/logout")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "unauthorized")
