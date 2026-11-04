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

    def test_quotation_upload_endpoint_accepts_csv(self):
        csv_text = (
            "quotation_id,item_id,supplier_name,unit_price,quantity_available,delivery_terms,quotation_valid_until,notes\n"
            "Q-999,ITEM-004,Uploaded Supplier Ltd,50000,50,Next-day delivery,2026-12-31,Demo quote\n"
        )
        response = self.client.post(
            "/api/quotations/upload",
            files={"file": ("quotes_demo.csv", csv_text, "text/csv")},
        )
        self.assertEqual(response.status_code, 200, response.text)
        payload = response.json()
        self.assertEqual(payload["status"], "uploaded")
        self.assertEqual(payload["quotes_loaded"], 1)

        quotes = self.client.get("/api/items/ITEM-004/quotes")
        self.assertEqual(quotes.status_code, 200)
        self.assertTrue(any(q["quotation_id"] == "Q-999" for q in quotes.json()["quotations"]))

        reset = self.client.post("/api/quotations/reset")
        self.assertEqual(reset.status_code, 200)

    def test_quotation_upload_accepts_common_header_variants(self):
        csv_text = (
            "quote_id,item,Vendor,price_ugx,available_qty,delivery_method,valid_until,remarks\n"
            "Q-777,ITEM-004,New Market Traders,42000,90,Same-day dispatch,2026-11-15,Alternate format\n"
        )
        response = self.client.post(
            "/api/quotations/upload",
            files={"file": ("quotes_alt.csv", csv_text, "text/csv")},
        )
        self.assertEqual(response.status_code, 200, response.text)
        payload = response.json()
        self.assertEqual(payload["status"], "uploaded")
        self.assertEqual(payload["quotes_loaded"], 1)

        quotes = self.client.get("/api/items/ITEM-004/quotes")
        self.assertEqual(quotes.status_code, 200)
        self.assertTrue(any(q["quotation_id"] == "Q-777" for q in quotes.json()["quotations"]))

        reset = self.client.post("/api/quotations/reset")
        self.assertEqual(reset.status_code, 200)

    def test_evaluation_uses_default_benchmark_not_uploaded_demo_data(self):
        inventory_csv = "item_id,item_name,category,current_stock,reorder_threshold,unit\nITEM-999,Uploaded Widget,Office Supplies,100,1,Box\n"
        quotes_csv = (
            "quotation_id,item_id,supplier_name,unit_price,quantity_available,delivery_terms,quotation_valid_until,notes\n"
            "Q-999,ITEM-004,Uploaded Supplier Ltd,100,50,Next-day delivery,2026-12-31,Demo quote\n"
        )

        upload_inventory = self.client.post(
            "/api/inventory/upload",
            files={"file": ("upload_benchmark_override.csv", inventory_csv, "text/csv")},
        )
        self.assertEqual(upload_inventory.status_code, 200, upload_inventory.text)

        upload_quotes = self.client.post(
            "/api/quotations/upload",
            files={"file": ("quotes_benchmark_override.csv", quotes_csv, "text/csv")},
        )
        self.assertEqual(upload_quotes.status_code, 200, upload_quotes.text)

        evaluation = self.client.get("/api/evaluation")
        self.assertEqual(evaluation.status_code, 200, evaluation.text)
        self.assertEqual(evaluation.json()["passed"], 32)
        self.assertEqual(evaluation.json()["failed"], 0)

        self.client.post("/api/inventory/reset")
        self.client.post("/api/quotations/reset")


if __name__ == "__main__":
    unittest.main()
