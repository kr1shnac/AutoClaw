import os
import sys
import json
import unittest
import tempfile

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Patch the env before importing security
os.environ["AUTHORIZED_TELEGRAM_IDS"] = "111111111,222222222"

from telegram.security import is_authorized, get_authorized_ids

class TestWhitelist(unittest.TestCase):

    def test_authorized_user_passes(self):
        self.assertTrue(is_authorized(111111111))
        self.assertTrue(is_authorized(222222222))

    def test_unauthorized_user_blocked(self):
        self.assertFalse(is_authorized(999999999))
        self.assertFalse(is_authorized(0))

    def test_get_authorized_ids_returns_set(self):
        ids = get_authorized_ids()
        self.assertIsInstance(ids, set)
        self.assertIn(111111111, ids)

    def test_non_numeric_ids_ignored(self):
        os.environ["AUTHORIZED_TELEGRAM_IDS"] = "111111111,bad_id,222222222"
        ids = get_authorized_ids()
        self.assertIn(111111111, ids)
        self.assertIn(222222222, ids)
        self.assertEqual(len(ids), 2)


class TestTimeoutLogic(unittest.TestCase):
    """
    Tests the timeout logic by verifying the SKIP fallback path.
    We simulate this by importing the wait logic and mocking time.
    """

    def test_skip_returned_on_no_response(self):
        """
        Verify that if no APPROVE/SKIP command arrives within the window,
        the function returns 'SKIP' by default.
        """
        # We mock the core utilities to avoid actual network calls
        import telegram.queue_poller as qp

        # Override dependencies for isolated test
        qp.fetch_commands_from_cloud = lambda: []
        qp.send_telegram_message = lambda chat_id, text: None
        qp._read_local_queue = lambda: []
        qp._write_local_queue = lambda q: None

        result = qp.wait_for_human_approval(
            job_info={"company": "TestCorp", "title": "Engineer"},
            operator_chat_id=111111111,
            timeout_seconds=1  # 1 second for test speed
        )

        self.assertEqual(result, "SKIP")


if __name__ == '__main__':
    unittest.main()
