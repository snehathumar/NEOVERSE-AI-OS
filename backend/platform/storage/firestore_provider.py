import os
import logging
import threading
import atexit
from typing import Dict, Any, List, Optional, Callable
from backend.platform.storage.manager import StorageManager
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

logger = logging.getLogger(__name__)

class FirestoreProvider(StorageManager):
    """
    Firestore implementation of the StorageManager.
    Used for production cloud storage.
    """
    def __init__(self, project_id: str = None):
        self._write_buffer = []
        self._buffer_lock = threading.Lock()
        self._batch_threshold = 50
        
        try:
            from google.cloud import firestore
            self.db = firestore.Client(project=project_id)
            self.transactional = firestore.transactional
            # Register atexit flush
            atexit.register(self.flush)
        except ImportError:
            raise Exception("google-cloud-firestore is not installed.")
        except Exception as e:
            raise Exception(f"Failed to initialize Firestore Client: {e}")

    def health_check(self) -> bool:
        """Pings Firestore to ensure connection is active."""
        if not hasattr(self, 'db'): return False
        try:
            # Just do a cheap metadata query or list collections limit 1
            list(self.db.collections(limit=1))
            return True
        except Exception:
            return False

    def flush(self):
        """Flushes any pending writes in the buffer to Firestore."""
        with self._buffer_lock:
            if not self._write_buffer:
                return
            
            try:
                batch = self.db.batch()
                for w in self._write_buffer:
                    doc_ref = self.db.collection(w['coll_name']).document(w['document_id'])
                    batch.set(doc_ref, w['data'])
                batch.commit()
                logger.debug(f"Flushed {len(self._write_buffer)} items to Firestore.")
            except Exception as e:
                logger.error(f"Failed to flush Firestore buffer: {e}")
            finally:
                self._write_buffer.clear()

    def _get_collection(self, collection: str) -> str:
        if not collection.startswith("neoverse_"):
            return f"neoverse_{collection}"
        return collection

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=1, max=10))
    def save(self, collection: str, document_id: str, data: Dict[str, Any]) -> str:
        coll_name = self._get_collection(collection)
        with self._buffer_lock:
            self._write_buffer.append({
                "coll_name": coll_name,
                "document_id": document_id,
                "data": data
            })
            should_flush = len(self._write_buffer) >= self._batch_threshold
        
        if should_flush:
            self.flush()
            
        return document_id

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=1, max=10))
    def get(self, collection: str, document_id: str) -> Optional[Dict[str, Any]]:
        self.flush() # Ensure we don't miss pending writes
        coll_name = self._get_collection(collection)
        doc_ref = self.db.collection(coll_name).document(document_id)
        doc = doc_ref.get()
        if doc.exists:
            return doc.to_dict()
        return None

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=1, max=10))
    def update(self, collection: str, document_id: str, data: Dict[str, Any]) -> bool:
        coll_name = self._get_collection(collection)
        doc_ref = self.db.collection(coll_name).document(document_id)
        if not doc_ref.get().exists:
            return False
        doc_ref.update(data)
        return True

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=1, max=10))
    def delete(self, collection: str, document_id: str) -> bool:
        coll_name = self._get_collection(collection)
        doc_ref = self.db.collection(coll_name).document(document_id)
        doc_ref.delete()
        return True

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=1, max=10))
    def query(self, collection: str, filters: Dict[str, Any] = None, order_by: str = None, limit: int = None) -> List[Dict[str, Any]]:
        self.flush()
        coll_name = self._get_collection(collection)
        query_ref = self.db.collection(coll_name)
        
        if filters:
            for k, v in filters.items():
                query_ref = query_ref.where(k, '==', v)
                
        if order_by:
            from google.cloud.firestore_v1.base_query import Direction
            query_ref = query_ref.order_by(order_by, direction=Direction.DESCENDING)
            
        if limit:
            query_ref = query_ref.limit(limit)
            
        docs = query_ref.stream()
        results = []
        for doc in docs:
            d = doc.to_dict()
            d['_id'] = doc.id
            results.append(d)
            
        return results

    def batch_write(self, writes: List[Dict[str, Any]]) -> bool:
        """
        Executes a batch of writes.
        writes format: [{"collection": "users", "id": "1", "data": {...}, "action": "set"|"update"|"delete"}]
        """
        try:
            batch = self.db.batch()
            for w in writes:
                coll_name = self._get_collection(w['collection'])
                doc_ref = self.db.collection(coll_name).document(w['id'])
                action = w.get('action', 'set')
                if action == 'set':
                    batch.set(doc_ref, w['data'])
                elif action == 'update':
                    batch.update(doc_ref, w['data'])
                elif action == 'delete':
                    batch.delete(doc_ref)
            batch.commit()
            return True
        except Exception as e:
            logger.error(f"Firestore batch write failed: {e}")
            raise e

    def run_transaction(self, callback: Callable) -> Any:
        """
        Executes a callback within a Firestore transaction.
        The callback must accept (transaction, db).
        """
        transaction = self.db.transaction()
        @self.transactional
        def _txn(transaction, *args, **kwargs):
            return callback(transaction, self.db, *args, **kwargs)
        return _txn(transaction)

    def _save_entity(self, collection: str, entity: Any) -> Any:
        data_dict = entity.model_dump(mode='json')
        self.save(collection, getattr(entity, 'id', str(id(entity))), data_dict)
        return entity

    def initialize(self):
        pass

    def save_user(self, user): return self._save_entity("users", user)
    def save_session(self, session): return self._save_entity("sessions", session)
    def save_message(self, message): return self._save_entity("messages", message)
    def save_decision(self, decision): return self._save_entity("decisions", decision)
    def save_universe(self, universe): return self._save_entity("universes", universe)
    def save_debate(self, debate): return self._save_entity("debates", debate)
    def save_report(self, report): return self._save_entity("reports", report)
    def save_event(self, event): return self._save_entity("events", event)
    def save_memory(self, memory): return self._save_entity("memories", memory)
    def save_learning(self, learning): return self._save_entity("learnings", learning)
    def save_monitoring(self, monitoring): return self._save_entity("monitoring", monitoring)
    def save_analytics(self, analytics): return self._save_entity("analytics", analytics)

    def get_history(self, session_id: str) -> List[Any]:
        return self.query("messages", {"session_id": session_id})
    
    def search(self, collection: str, query: Dict[str, Any]) -> List[Any]:
        return self.query(collection, query)
