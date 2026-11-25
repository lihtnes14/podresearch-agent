import unittest
from uuid import uuid4

from backend.memory.session_memory import (
    create_session,
    get_session,
    list_sessions,
    update_session,
    delete_session,
    save_artifact,
    get_artifacts,
    get_latest_artifact,
)


class TestSessionMemory(unittest.TestCase):
    def setUp(self):
        self.session_title = f"Test Session {uuid4().hex[:6]}"
        self.session_url = f"https://youtu.be/{uuid4().hex[:8]}"
        self.session = create_session(
            title=self.session_title,
            podcast_url=self.session_url,
        )

    def tearDown(self):
        delete_session(self.session.id)

    def test_create_and_get_session(self):
        fetched = get_session(self.session.id)
        self.assertIsNotNone(fetched)
        self.assertEqual(fetched.title, self.session_title)
        self.assertEqual(fetched.podcast_url, self.session_url)
        self.assertEqual(fetched.status, "created")

    def test_list_sessions(self):
        sessions = list_sessions()
        self.assertTrue(any(s.id == self.session.id for s in sessions))

    def test_update_session(self):
        updated = update_session(
            self.session.id,
            title="Updated Title",
            status="article_ready",
        )
        self.assertEqual(updated.title, "Updated Title")
        self.assertEqual(updated.status, "article_ready")

        fetched = get_session(self.session.id)
        self.assertEqual(fetched.status, "article_ready")

    def test_artifacts_save_and_retrieve_latest(self):
        # Save first version of article
        art1 = save_artifact(
            session_id=self.session.id,
            artifact_type="article",
            content='{"version": 1}',
        )
        # Save second version of article
        art2 = save_artifact(
            session_id=self.session.id,
            artifact_type="article",
            content='{"version": 2}',
        )
        # Save guardrail artifact
        save_artifact(
            session_id=self.session.id,
            artifact_type="guardrail",
            content='{"passed": true}',
        )

        all_artifacts = get_artifacts(self.session.id)
        self.assertEqual(len(all_artifacts), 3)

        # get_latest_artifact must return the newest version (art2)
        latest_article = get_latest_artifact(self.session.id, "article")
        self.assertIsNotNone(latest_article)
        self.assertEqual(latest_article.content, '{"version": 2}')

    def test_delete_session_removes_artifacts(self):
        save_artifact(
            session_id=self.session.id,
            artifact_type="transcript",
            content="sample transcript",
        )
        self.assertEqual(len(get_artifacts(self.session.id)), 1)

        # Delete session
        deleted = delete_session(self.session.id)
        self.assertTrue(deleted)

        # Both session and artifacts should be deleted
        self.assertIsNone(get_session(self.session.id))
        self.assertEqual(len(get_artifacts(self.session.id)), 0)


if __name__ == "__main__":
    unittest.main()

