import unittest
from unittest.mock import patch
from backend.memory.api import MemoryAPI
from backend.memory.models import ConversationMemory, DecisionMemory, LearningMemory
from backend.platform.storage.sqlite_provider import SQLiteStorage

class TestCognitiveMemorySystem(unittest.TestCase):
    def setUp(self):
        # Fresh in-memory DB per test
        self.test_storage = SQLiteStorage(db_path=":memory:")
        
        # Patch where the manager ACTUALLY imports get_storage_manager
        patcher = patch('backend.memory.manager.get_storage_manager', return_value=self.test_storage)
        self.addCleanup(patcher.stop)
        patcher.start()
        
        self.api = MemoryAPI(user_id="test_user")

    def test_persistence_and_multi_tenancy(self):
        # Create memory for test_user
        mem1 = ConversationMemory(content="User 1 says hello")
        self.api.remember(mem1)
        
        # Verify test_user can retrieve it
        results = self.api.retrieve("conversation")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].content, "User 1 says hello")
        self.assertEqual(results[0].user_id, "test_user")
        
        # Verify another user cannot see it
        api_other = MemoryAPI(user_id="hacker_user")
        results_other = api_other.retrieve("conversation")
        self.assertEqual(len(results_other), 0)

    def test_memory_graph_relationships(self):
        # Create a conversation
        conv = ConversationMemory(content="What should we build?")
        saved_conv = self.api.remember(conv)
        
        # Create a decision linked to conversation
        dec = DecisionMemory(
            original_question="What should we build?",
            business_context="Software",
            recommendation="Build AI",
            related_memory_ids=[saved_conv.id]
        )
        saved_dec = self.api.remember(dec)
        
        # Retrieve related
        related_decisions = self.api.retrieve_related("decision", saved_conv.id)
        self.assertEqual(len(related_decisions), 1)
        self.assertEqual(related_decisions[0].id, saved_dec.id)

    def test_retrieval_ranking(self):
        # Insert memories with varying importance
        for i in range(5):
            m = DecisionMemory(
                original_question=f"Q{i}", 
                business_context="C", 
                recommendation="R",
                importance_score=10 * i  # 0, 10, 20, 30, 40
            )
            self.api.remember(m)
            
        important = self.api.manager.retrieve_important("decision", min_importance=25, limit=2)
        # Should return importance 40, then 30
        self.assertEqual(len(important), 2)
        self.assertEqual(important[0].importance_score, 40)
        self.assertEqual(important[1].importance_score, 30)

    def test_archive_and_restore(self):
        mem = ConversationMemory(content="Test archive")
        saved = self.api.remember(mem)
        
        # Verify active
        results = self.api.retrieve("conversation")
        self.assertEqual(len(results), 1)
        
        # Archive
        self.api.archive("conversation", saved.id)
        
        # Verify no longer active
        results_archived = self.api.retrieve("conversation")
        self.assertEqual(len(results_archived), 0)
        
        # Restore
        self.api.restore("conversation", saved.id)
        results_restored = self.api.retrieve("conversation")
        self.assertEqual(len(results_restored), 1)

    def test_learning_evolution(self):
        dec = DecisionMemory(original_question="Q", business_context="B", recommendation="R")
        saved = self.api.remember(dec)
        
        # Trigger learning
        self.api.learn(saved.id)
        
        learnings = self.api.retrieve("learning")
        self.assertEqual(len(learnings), 1)
        self.assertIn(saved.id, learnings[0].related_memory_ids)

if __name__ == '__main__':
    unittest.main()
