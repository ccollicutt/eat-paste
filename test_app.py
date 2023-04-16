import unittest
from app import app, get_collection
import mongomock


class TestPasteAPI(unittest.TestCase):
    def setUp(self):
        app.config["TESTING"] = True
        self.app = app.test_client()
        self.mongo_client = mongomock.MongoClient()
        app.set_mongo_client(self.mongo_client)

    def test_paste_creation(self):
        response = self.app.post(
            "/paste", data="Test content", content_type="text/plain"
        )
        self.assertEqual(response.status_code, 200)

    def test_paste_too_large(self):
        large_data = "a" * 10001
        response = self.app.post("/paste", data=large_data, content_type="text/plain")
        self.assertEqual(response.status_code, 413)

    def test_paste_empty(self):
        response = self.app.post("/paste", data="", content_type="text/plain")
        self.assertEqual(response.status_code, 400)

    def test_paste_wrong_content_type(self):
        response = self.app.post(
            "/paste", data="Test content", content_type="application/json"
        )
        self.assertEqual(response.status_code, 400)

    def test_paste_html_in_request_data(self):
        response = self.app.post(
            "/paste",
            data="<script>alert('XSS attack!')</script>",
            content_type="text/plain",
        )
        self.assertEqual(response.status_code, 400)

    def test_get_paste(self):
        # Create a paste
        response = self.app.post(
            "/paste", data="Test content", content_type="text/plain"
        )
        slug = response.data.decode()
        print("slug is", slug)

        # Retrieve the paste
        response = self.app.get(f"/paste/{slug}")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data.decode(), "Test content")

    def test_get_paste_not_found(self):
        response = self.app.get("/paste/nonexistent-slug")
        self.assertEqual(response.status_code, 404)

    def test_invalid_slug(self):
        # slug must be word-word format
        response = self.app.get("/paste/invalid_sluggy_slug")
        self.assertEqual(response.status_code, 500)


if __name__ == "__main__":
    unittest.main()
