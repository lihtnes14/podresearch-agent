import json
import unittest
from fastapi.testclient import TestClient

from backend.main import app
from backend.memory.database import Base, engine
from backend.memory.session_memory import save_artifact, delete_session


class TestPodResearchAPI(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        Base.metadata.create_all(bind=engine)
        cls.client = TestClient(app)

    def test_01_health_check(self):
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "ok")
        self.assertIn("PodResearch", data["app"])

    def test_02_session_lifecycle(self):
        # 1. Create session
        create_res = self.client.post(
            "/api/sessions",
            json={
                "title": "API Test Session",
                "podcast_url": "https://youtu.be/test12345",
            },
        )
        self.assertEqual(create_res.status_code, 201)
        session_data = create_res.json()
        session_id = session_data["id"]
        self.assertEqual(session_data["title"], "API Test Session")

        # 2. List sessions
        list_res = self.client.get("/api/sessions")
        self.assertEqual(list_res.status_code, 200)
        sessions = list_res.json()
        self.assertTrue(any(s["id"] == session_id for s in sessions))

        # 3. Get session details
        get_res = self.client.get(f"/api/sessions/{session_id}")
        self.assertEqual(get_res.status_code, 200)
        detail = get_res.json()
        self.assertEqual(detail["session"]["id"], session_id)
        self.assertIsInstance(detail["artifacts"], list)

        # 4. Patch / update session
        patch_res = self.client.patch(
            f"/api/sessions/{session_id}",
            json={"title": "Updated API Title"},
        )
        self.assertEqual(patch_res.status_code, 200)
        self.assertEqual(patch_res.json()["title"], "Updated API Title")

        # 5. Delete session
        del_res = self.client.delete(f"/api/sessions/{session_id}")
        self.assertEqual(del_res.status_code, 204)

        # 6. Verify 404 after deletion
        verify_res = self.client.get(f"/api/sessions/{session_id}")
        self.assertEqual(verify_res.status_code, 404)

    def test_03_artifacts_api(self):
        # Create session
        create_res = self.client.post(
            "/api/sessions",
            json={"title": "Artifacts Test", "podcast_url": "https://youtu.be/artifacts"},
        )
        session_id = create_res.json()["id"]

        try:
            # Save test artifacts directly in memory
            article_payload = {"title": "Test Title", "article": "Test body"}
            save_artifact(session_id, "article", json.dumps(article_payload))
            save_artifact(session_id, "transcript", "[00:00] Test transcript")

            # 1. Fetch all artifacts
            art_res = self.client.get(f"/api/sessions/{session_id}/artifacts")
            self.assertEqual(art_res.status_code, 200)
            artifacts = art_res.json()
            self.assertEqual(len(artifacts), 2)

            # 2. Fetch specific artifact type
            latest_res = self.client.get(f"/api/sessions/{session_id}/artifacts/article")
            self.assertEqual(latest_res.status_code, 200)
            art_data = latest_res.json()
            self.assertEqual(art_data["artifact_type"], "article")
            self.assertEqual(art_data["data"]["title"], "Test Title")

            # 3. Fetch non-existent artifact type
            missing_res = self.client.get(f"/api/sessions/{session_id}/artifacts/nonexistent")
            self.assertEqual(missing_res.status_code, 404)

        finally:
            delete_session(session_id)

    def test_04_validation_errors(self):
        # Missing required field podcast_url
        res = self.client.post("/api/sessions", json={"title": "Only Title"})
        self.assertEqual(res.status_code, 422)


if __name__ == "__main__":
    unittest.main()
