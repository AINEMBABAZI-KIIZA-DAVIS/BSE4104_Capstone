import unittest

from fastapi.testclient import TestClient

from app import app


class RealApiSmokeTests(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_health_endpoint(self):
        response = self.client.get("/api/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "ok")

    def test_item_status_endpoint(self):
        response = self.client.get("/api/items/ITEM-004/status")
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertIn("needs_reorder", payload)
        self.assertTrue(payload["needs_reorder"])

    def test_create_draft_endpoint(self):
        response = self.client.post(
            "/api/requisitions/draft",
            json={
                "item_id": "ITEM-004",
                "quantity": 10,
                "selected_quotation_id": "Q-107",
                "requested_by": "Jane Okello",
            },
        )
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertIn("requisition_id", payload)
        self.assertEqual(payload["status"], "DRAFT")


if __name__ == "__main__":
    unittest.main()
