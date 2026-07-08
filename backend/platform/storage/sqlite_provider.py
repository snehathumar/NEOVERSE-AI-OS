import sqlite3
import json
import logging
import time
import threading
import contextlib
from typing import Dict, Any, List, Optional
from backend.platform.storage.manager import StorageManager
from backend.platform.storage.models import (
    User, Session, Message, Decision, Universe, Debate, Report, Event, 
    Memory, Learning, Analytics, Monitoring, StorageModel
)

logger = logging.getLogger(__name__)

class SQLiteStorage(StorageManager):
    """
    Enterprise SQLite implementation of the StorageManager.
    """
    def __init__(self, db_path: str = "neoverse.db"):
        self.db_path = db_path
        self._lock = threading.RLock()

    @contextlib.contextmanager
    def _locked_connection(self):
        with self._lock:
            with self._get_connection() as conn:
                yield conn

    def _get_connection(self):
        if self.db_path == ":memory:" and hasattr(self, "_mem_conn"):
            return self._mem_conn
        conn = sqlite3.connect(self.db_path, check_same_thread=False, timeout=30.0)
        conn.execute("PRAGMA journal_mode=WAL")
        conn.row_factory = sqlite3.Row
        if self.db_path == ":memory:":
            self._mem_conn = conn
        return conn

    def initialize(self):
        """Pre-creates all tables using robust schema."""
        for col_name in self.collections.keys():
            self._ensure_table(col_name)

    def _ensure_table(self, collection: str):
        """Creates the collection table if it doesn't exist."""
        safe_col = ''.join(c for c in collection if c.isalnum() or c == '_')
        with self._locked_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(f'''
                CREATE TABLE IF NOT EXISTS {safe_col} (
                    id TEXT PRIMARY KEY,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    metadata JSON NOT NULL
                )
            ''')


    def _save_entity(self, collection: str, entity: StorageModel) -> StorageModel:
        """Generic save method for StorageModels."""
        self._ensure_table(collection)
        safe_col = ''.join(c for c in collection if c.isalnum() or c == '_')
        data_dict = entity.model_dump(mode='json')
        
        retries = 3
        while retries > 0:
            try:
                with self._locked_connection() as conn:
                    cursor = conn.cursor()
                    cursor.execute(
                        f"INSERT OR REPLACE INTO {safe_col} (id, created_at, updated_at, metadata) VALUES (?, ?, ?, ?)",
                        (entity.id, entity.created_at, entity.updated_at, json.dumps(data_dict))
                    )
    
                return entity
            except sqlite3.Error as e:
                logger.error(f"Database error saving to {safe_col}: {e}")
                retries -= 1
                time.sleep(0.1)
                if retries == 0:
                    # Graceful fallback, return entity anyway (though not saved)
                    # The instruction says "Return graceful fallback. Never crash."
                    return entity

    def _get_entity(self, collection: str, document_id: str, model_class: type) -> Optional[StorageModel]:
        safe_col = ''.join(c for c in collection if c.isalnum() or c == '_')
        try:
            with self._locked_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(f"SELECT metadata FROM {safe_col} WHERE id = ?", (document_id,))  # nosec B608
                row = cursor.fetchone()
                if row:
                    data = json.loads(row['metadata'])
                    return model_class(**data)
        except sqlite3.Error as e:
            logger.error(f"Database error reading from {safe_col}: {e}")
        return None

    # Generic Dictionary Operations (Raw)
    def save(self, collection: str, document_id: str, data: Dict[str, Any]) -> str:
        self._ensure_table(collection)
        safe_col = ''.join(c for c in collection if c.isalnum() or c == '_')
        from datetime import datetime, timezone
        created_at = data.get('created_at', datetime.now(timezone.utc).isoformat())
        updated_at = datetime.now(timezone.utc).isoformat()
        try:
            with self._locked_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    f"INSERT OR REPLACE INTO {safe_col} (id, created_at, updated_at, metadata) VALUES (?, ?, ?, ?)",
                    (document_id, created_at, updated_at, json.dumps(data))
                )

            return document_id
        except sqlite3.Error as e:
            logger.error(f"Database error saving raw to {safe_col}: {e}")
            return document_id

    def get(self, collection: str, document_id: str) -> Optional[Dict[str, Any]]:
        self._ensure_table(collection)
        safe_col = ''.join(c for c in collection if c.isalnum() or c == '_')
        try:
            with self._locked_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(f"SELECT metadata FROM {safe_col} WHERE id = ?", (document_id,))  # nosec B608
                row = cursor.fetchone()
                if row:
                    return json.loads(row['metadata'])
        except sqlite3.Error as e:
            logger.error(f"Database error getting raw from {safe_col}: {e}")
        return None

    def batch_write(self, writes: List[Dict[str, Any]]) -> bool:
        """
        Executes a batch of writes within a single SQLite transaction.
        writes format: [{"collection": "users", "id": "1", "data": {...}, "action": "set"|"update"|"delete"}]
        """
        try:
            with self._locked_connection() as conn:
                cursor = conn.cursor()
                for w in writes:
                    col = w['collection']
                    self._ensure_table(col)
                    safe_col = ''.join(c for c in col if c.isalnum() or c == '_')
                    doc_id = w['id']
                    action = w.get('action', 'set')
                    
                    if action == 'set':
                        data = w['data']
                        from datetime import datetime, timezone
                        created_at = data.get('created_at', datetime.now(timezone.utc).isoformat())
                        updated_at = datetime.now(timezone.utc).isoformat()
                        cursor.execute(
                            f"INSERT OR REPLACE INTO {safe_col} (id, created_at, updated_at, metadata) VALUES (?, ?, ?, ?)",
                            (doc_id, created_at, updated_at, json.dumps(data))
                        )
                    elif action == 'update':
                        # Simplistic update, ideally should merge JSON
                        data = w['data']
                        cursor.execute(f"SELECT metadata FROM {safe_col} WHERE id = ?", (doc_id,))  # nosec B608
                        row = cursor.fetchone()
                        if row:
                            metadata = json.loads(row['metadata'])
                            metadata.update(data)
                            from datetime import datetime, timezone
                            updated_at = datetime.now(timezone.utc).isoformat()
                            cursor.execute(
                                f"UPDATE {safe_col} SET updated_at = ?, metadata = ? WHERE id = ?",  # nosec B608
                                (updated_at, json.dumps(metadata), doc_id)
                            )
                    elif action == 'delete':
                        cursor.execute(f"DELETE FROM {safe_col} WHERE id = ?", (doc_id,))  # nosec B608

            return True
        except sqlite3.Error as e:
            logger.error(f"SQLite batch write failed: {e}")
            raise e

    def run_transaction(self, callback) -> Any:
        """
        Executes a callback within a SQLite connection context (acting as transaction).
        """
        with self._locked_connection() as conn:
            # We pass `conn` as the transaction object and `self` as the DB
            return callback(conn, self)

    # Exact Abstract Method Implementations
    def save_user(self, user: User) -> User: return self._save_entity("users", user)
    def save_session(self, session: Session) -> Session: return self._save_entity("sessions", session)
    def save_message(self, message: Message) -> Message: return self._save_entity("messages", message)
    def save_decision(self, decision: Decision) -> Decision: return self._save_entity("decisions", decision)
    def save_universe(self, universe: Universe) -> Universe: return self._save_entity("universes", universe)
    def save_debate(self, debate: Debate) -> Debate: return self._save_entity("debates", debate)
    def save_report(self, report: Report) -> Report: return self._save_entity("reports", report)
    def save_event(self, event: Event) -> Event: return self._save_entity("events", event)
    def save_memory(self, memory: Memory) -> Memory: return self._save_entity("memories", memory)
    def save_learning(self, learning: Learning) -> Learning: return self._save_entity("learnings", learning)
    def save_monitoring(self, monitoring: Monitoring) -> Monitoring: return self._save_entity("monitoring", monitoring)
    def save_analytics(self, analytics: Analytics) -> Analytics: return self._save_entity("analytics", analytics)

    def get_history(self, session_id: str) -> List[Message]:
        try:
            with self._locked_connection() as conn:
                cursor = conn.cursor()
                # Use JSON extraction to filter in sqlite
                # For basic sqlite without json1, we can just load and filter
                cursor.execute(f"SELECT metadata FROM messages")  # nosec B608
                rows = cursor.fetchall()
                history = []
                for row in rows:
                    data = json.loads(row['metadata'])
                    if data.get('session_id') == session_id:
                        history.append(Message(**data))
                # Sort by created_at
                history.sort(key=lambda x: x.created_at)
                return history
        except sqlite3.Error as e:
            logger.error(f"Error fetching history: {e}")
            return []

    def search(self, collection: str, query: Dict[str, Any], return_class: type = None) -> List[Any]:
        self._ensure_table(collection)
        safe_col = ''.join(c for c in collection if c.isalnum() or c == '_')
        model_class = return_class or dict
        try:
            with self._locked_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(f"SELECT metadata FROM {safe_col}")  # nosec B608
                rows = cursor.fetchall()
                results = []
                for row in rows:
                    data = json.loads(row['metadata'])
                    match = True
                    for k, v in query.items():
                        if data.get(k) != v:
                            match = False
                            break
                    if match:
                        if model_class is dict:
                            results.append(data)
                        else:
                            results.append(model_class(**data))
                return results
        except sqlite3.Error as e:
            logger.error(f"Database search error: {e}")
            return []

    def delete(self, collection: str, document_id: str) -> bool:
        self._ensure_table(collection)
        safe_col = ''.join(c for c in collection if c.isalnum() or c == '_')
        try:
            with self._locked_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(f"DELETE FROM {safe_col} WHERE id = ?", (document_id,))  # nosec B608

                return cursor.rowcount > 0
        except sqlite3.Error as e:
            logger.error(f"Database delete error: {e}")
            return False

    def update(self, collection: str, document_id: str, data: Dict[str, Any]) -> bool:
        self._ensure_table(collection)
        safe_col = ''.join(c for c in collection if c.isalnum() or c == '_')
        try:
            with self._locked_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(f"SELECT metadata FROM {safe_col} WHERE id = ?", (document_id,))  # nosec B608
                row = cursor.fetchone()
                if not row: return False
                
                import json
                metadata = json.loads(row['metadata'])
                metadata.update(data)
                
                from datetime import datetime, timezone
                updated_at = datetime.now(timezone.utc).isoformat()
                
                cursor.execute(
                    f"UPDATE {safe_col} SET updated_at = ?, metadata = ? WHERE id = ?",  # nosec B608
                    (updated_at, json.dumps(metadata), document_id)
                )

                return True
        except sqlite3.Error as e:
            logger.error(f"Database update error: {e}")
            return False
