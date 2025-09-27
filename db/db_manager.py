import os
import sqlite3
from typing import Optional, Dict, Any

class DBManager:
    """
    评分库管理：SQLite
    - 表：fortune_scores
        id          INTEGER PRIMARY KEY AUTOINCREMENT
        dimension   TEXT NOT NULL          -- 维度（当前只用“流日”）
        key         TEXT NOT NULL          -- 唯一键（流日用 YYYY-MM-DD，Asia/Shanghai）
        emotion     INTEGER NOT NULL
        health      INTEGER NOT NULL
        wealth      INTEGER NOT NULL
        source      TEXT                   -- 数据来源：db/model
        created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        updated_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
      UNIQUE (dimension, key)
    """

    def __init__(self, db_path: Optional[str] = None) -> None:
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.db_path = db_path or os.path.join(project_root, "db", "fortune_scores.sqlite3")
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self._init_schema()

    def _init_schema(self) -> None:
        cur = self.conn.cursor()
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS fortune_scores (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                dimension TEXT NOT NULL,
                "key" TEXT NOT NULL,
                emotion INTEGER NOT NULL,
                health INTEGER NOT NULL,
                wealth INTEGER NOT NULL,
                source TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE (dimension, "key")
            )
            """
        )
        self.conn.commit()

    def get_score(self, dimension: str, key: str) -> Optional[Dict[str, Any]]:
        cur = self.conn.cursor()
        cur.execute(
            'SELECT emotion, health, wealth, source, created_at, updated_at FROM fortune_scores WHERE dimension=? AND "key"=?',
            (dimension, key),
        )
        row = cur.fetchone()
        if not row:
            return None
        return {
            "emotion": int(row["emotion"]),
            "health": int(row["health"]),
            "wealth": int(row["wealth"]),
            "source": row["source"] or "db",
            "created_at": row["created_at"],
            "updated_at": row["updated_at"],
        }

    def upsert_score(self, dimension: str, key: str, scores: Dict[str, int], source: str = "model") -> None:
        cur = self.conn.cursor()
        cur.execute(
            """
            INSERT INTO fortune_scores (dimension, "key", emotion, health, wealth, source, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            ON CONFLICT(dimension, "key") DO UPDATE SET
                emotion=excluded.emotion,
                health=excluded.health,
                wealth=excluded.wealth,
                source=excluded.source,
                updated_at=CURRENT_TIMESTAMP
            """,
            (
                dimension,
                key,
                int(scores["emotion"]),
                int(scores["health"]),
                int(scores["wealth"]),
                source,
            ),
        )
        self.conn.commit()

# 模块级单例
db = DBManager()