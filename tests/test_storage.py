import unittest
import uuid
import threading
from backend.platform.storage.sqlite_provider import SQLiteStorage
from backend.platform.storage.models import User, Session, Message, Decision

class TestEnterpriseStorage(unittest.TestCase):
    def setUp(self):
        # We use an in-memory database for testing
        self.storage = SQLiteStorage(db_path=":memory:")

    def test_schema_enforcement_and_insert(self):
        # Create a user model
        u = User(username="admin", email="admin@neoverse.ai")
        # Save user
        saved_user = self.storage.save_user(u)
        self.assertIsNotNone(saved_user.id)
        self.assertEqual(saved_user.username, "admin")
        
        # Verify it can be retrieved via search
        results = self.storage.search("users", {"username": "admin"})
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].email, "admin@neoverse.ai")

    def test_history_retrieval(self):
        session_id = str(uuid.uuid4())
        m1 = Message(session_id=session_id, role="user", content="Hello")
        m2 = Message(session_id=session_id, role="assistant", content="Hi")
        
        self.storage.save_message(m1)
        self.storage.save_message(m2)
        
        history = self.storage.get_history(session_id)
        self.assertEqual(len(history), 2)
        self.assertEqual(history[0].role, "user")
        self.assertEqual(history[1].role, "assistant")

    def test_update_and_delete(self):
        d = Decision(prompt="Launch product?", confidence=50, recommendation="Wait")
        self.storage.save_decision(d)
        
        # Update
        updated = self.storage.update("decisions", d.id, {"confidence": 99})
        self.assertTrue(updated)
        
        # Verify update
        results = self.storage.search("decisions", {"id": d.id})
        self.assertEqual(results[0].confidence, 99)
        
        # Delete
        deleted = self.storage.delete("decisions", d.id)
        self.assertTrue(deleted)
        
        results_after_delete = self.storage.search("decisions", {"id": d.id})
        self.assertEqual(len(results_after_delete), 0)

    def test_concurrent_writes(self):
        session_id = str(uuid.uuid4())
        
        def worker(msg_content):
            m = Message(session_id=session_id, role="user", content=msg_content)
            self.storage.save_message(m)
            
        threads = []
        for i in range(10):
            t = threading.Thread(target=worker, args=(f"Msg {i}",))
            threads.append(t)
            t.start()
            
        for t in threads:
            t.join()
            
        history = self.storage.get_history(session_id)
        self.assertEqual(len(history), 10)

if __name__ == '__main__':
    unittest.main()
