import unittest

from fastapi.testclient import TestClient

from app import app


class EvaluationEndpointTests(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_evaluation_endpoint_returns_live_run(self):
        response = self.client.get("/api/evaluation")
        self.assertEqual(response.status_code, 200, response.text)
        payload = response.json()
        self.assertEqual(payload["total"], 32)
        self.assertEqual(payload["passed"], 32)
        self.assertEqual(len(payload["rows"]), 32)
        self.assertEqual(payload["rows"][0]["id"], "EV-01")


if __name__ == "__main__":
    unittest.main()
