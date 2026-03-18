
from __future__ import annotations
import os
import psycopg2
from psycopg2.extras import RealDictCursor

class DatabaseEngine:

    def __init__(self, config: dict):
        self.config = config

    def connect(self):
        return psycopg2.connect(
            host=self.config.get("host"),
            port=self.config.get("port"),
            dbname=self.config.get("database"),
            user=self.config.get("user"),
            password=self.config.get("password"),
            cursor_factory=RealDictCursor
        )

    def test_connection(self):
        conn = self.connect()
        cur = conn.cursor()
        cur.execute("SELECT 1 as ok")
        result = cur.fetchone()
        conn.close()
        return result["ok"] == 1
