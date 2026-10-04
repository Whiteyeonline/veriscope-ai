"""
core/cache.py
Local SQLite Caching Layer to Preserve Free API Limits
"""
import sqlite3
import json
import os
import hashlib
from typing import Optional, Dict, Any

class SQLiteCache:
    def __init__(self, db_path: str = "cache/audit_cache.db"):
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS api_cache (
                    key TEXT PRIMARY KEY,
                    response TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

    def _hash_key(self, query: str) -> str:
        return hashlib.sha256(query.encode('utf-8')).hexdigest()

    def get(self, query: str) -> Optional[Dict[str, Any]]:
        key = self._hash_key(query)
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT response FROM api_cache WHERE key = ?", (key,))
            row = cursor.fetchone()
            if row:
                return json.loads(row[0])
        return None

    def set(self, query: str, data: Dict[str, Any]):
        key = self._hash_key(query)
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "INSERT OR REPLACE INTO api_cache (key, response) VALUES (?, ?)",
                (key, json.dumps(data))
            )
