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

    def test_demo_users_are_available(self):
        response = self.client.get("/api/demo-users")
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertIn("users", payload)
        self.assertGreaterEqual(len(payload["users"]), 3)

    def test_approval_requires_valid_demo_user(self):
        draft = self.client.post(
            "/api/requisitions/draft",
            json={
                "item_id": "ITEM-004",
                "quantity": 3,
                "selected_quotation_id": "Q-107",
                "requested_by": "Jane Okello",
                "requested_by_user_id": "u-101",
            },
        )
        self.assertEqual(draft.status_code, 200)
        requisition_id = draft.json()["requisition_id"]

        response = self.client.post(
            f"/api/requisitions/{requisition_id}/approve",
            json={"approved_by_user_id": "u-999", "approved_by_role": "vendor"},
        )
        self.assertEqual(response.status_code, 400)
        payload = response.json()
        self.assertIn("error", payload)

    def test_inventory_upload_endpoint_accepts_csv(self):
        csv_text = "item_id,item_name,category,current_stock,reorder_threshold,unit\nITEM-999,Uploaded Widget,Office Supplies,4,10,Box\n"
        response = self.client.post(
            "/api/inventory/upload",
            files={"file": ("upload_demo.csv", csv_text, "text/csv")},
        )
        self.assertEqual(response.status_code, 200, response.text)
        payload = response.json()
        self.assertEqual(payload["status"], "uploaded")
        self.assertEqual(payload["items_loaded"], 1)

        status = self.client.get("/api/items/ITEM-999/status")
        self.assertEqual(status.status_code, 200)
        self.assertTrue(status.json()["needs_reorder"])

        reset = self.client.post("/api/inventory/reset")
        self.assertEqual(reset.status_code, 200)


if __name__ == "__main__":
    unittest.main()
