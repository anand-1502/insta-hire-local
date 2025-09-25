from sqlalchemy import create_engine, text
from pathlib import Path
from typing import List, Dict, Any
from src.settings import settings

class DB:
    def __init__(self):
        Path(settings.DATA_DIR).mkdir(parents=True, exist_ok=True)
        self.engine = create_engine(f"sqlite:///{settings.DB_PATH}", future=True)
        self._init_schema()

    def _init_schema(self):
        ddl = """
        CREATE TABLE IF NOT EXISTS candidates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            email TEXT,
            phone TEXT,
            city TEXT,
            state TEXT,
            pay_min REAL,
            pay_max REAL,
            availability TEXT,
            resume_path TEXT,
            resume_excerpt TEXT,
            embedding_id INTEGER
        );
        CREATE INDEX IF NOT EXISTS idx_candidates_embedding_id ON candidates(embedding_id);
        """
        with self.engine.begin() as conn:
            for stmt in ddl.strip().split(";"):
                if stmt.strip():
                    conn.execute(text(stmt))

    def add_candidate(self, **kwargs) -> int:
        fields = ", ".join(kwargs.keys())
        placeholders = ", ".join([f":{k}" for k in kwargs.keys()])
        sql = text(f"INSERT INTO candidates ({fields}) VALUES ({placeholders})")
        with self.engine.begin() as conn:
            res = conn.execute(sql, kwargs)
            cand_id = res.lastrowid
        return int(cand_id)

    def get_candidates_by_embedding_ids(self, emb_ids: List[int]) -> List[Dict[str, Any]]:
        if not emb_ids:
            return []
        placeholders = ", ".join(["?"] * len(emb_ids))
        sql = f"SELECT * FROM candidates WHERE embedding_id IN ({placeholders})"
        raw = self.engine.raw_connection()
        try:
            cur = raw.cursor()
            cur.execute(sql, emb_ids)
            cols = [c[0] for c in cur.description]
            rows = [dict(zip(cols, r)) for r in cur.fetchall()]
            cur.close()
        finally:
            raw.close()
        return rows

    def get_all_candidates(self) -> List[Dict[str, Any]]:
        with self.engine.connect() as conn:
            rows = conn.execute(text("SELECT * FROM candidates")).mappings().all()
            return [dict(r) for r in rows]

    def get_candidates_by_ids(self, ids: list[int]) -> list[dict]:
        if not ids:
            return []
        placeholders = ", ".join([f":id{i}" for i in range(len(ids))])
        sql = text(f"SELECT * FROM candidates WHERE id IN ({placeholders})")
        params = {f"id{i}": v for i, v in enumerate(ids)}
        with self.engine.connect() as conn:
            rows = conn.execute(sql, params).mappings().all()
            return [dict(r) for r in rows]

    def update_candidate_embedding(self, cand_id: int, emb_id: int):
        sql = text("UPDATE candidates SET embedding_id = :emb_id WHERE id = :cand_id")
        with self.engine.begin() as conn:
            conn.execute(sql, {"emb_id": emb_id, "cand_id": cand_id})
