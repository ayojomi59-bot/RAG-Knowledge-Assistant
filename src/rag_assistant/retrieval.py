import json
import math
import os
import re
import sqlite3
from uuid import uuid4

DB_PATH = os.getenv("RAG_DB_PATH", "rag_assistant.db")

def _connect():
    db = sqlite3.connect(DB_PATH)
    db.row_factory = sqlite3.Row
    db.execute("""CREATE TABLE IF NOT EXISTS chunks (
        id TEXT PRIMARY KEY, filename TEXT NOT NULL, chunk_index INTEGER NOT NULL,
        content TEXT NOT NULL, embedding TEXT)""")
    return db

def _embed(text: str):
    if not os.getenv("OPENAI_API_KEY"):
        return None
    from openai import OpenAI
    result = OpenAI().embeddings.create(
        model=os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small"), input=text)
    return result.data[0].embedding

def add_document(filename: str, chunks: list[str]) -> int:
    rows = []
    for index, content in enumerate(chunks):
        vector = _embed(content)
        rows.append((str(uuid4()), filename, index, content,
                     json.dumps(vector) if vector else None))
    with _connect() as db:
        db.executemany("INSERT INTO chunks VALUES(?,?,?,?,?)", rows)
    return len(rows)

def search(query: str, limit: int = 5) -> list[dict]:
    qvec = _embed(query)
    terms = set(re.findall(r"[a-z0-9]{2,}", query.lower()))
    with _connect() as db:
        rows = db.execute("SELECT * FROM chunks").fetchall()
    ranked = []
    for row in rows:
        if qvec and row["embedding"]:
            vec = json.loads(row["embedding"])
            denom = math.sqrt(sum(x*x for x in qvec) * sum(x*x for x in vec))
            score = sum(a*b for a, b in zip(qvec, vec)) / denom if denom else 0
        else:
            words = set(re.findall(r"[a-z0-9]{2,}", row["content"].lower()))
            score = len(terms & words) / math.sqrt(max(1, len(terms)) * max(1, len(words)))
        if score > 0:
            ranked.append((score, row))
    ranked.sort(key=lambda x: x[0], reverse=True)
    return [{"filename": r["filename"], "chunk_index": r["chunk_index"],
             "content": r["content"], "score": round(s, 4)} for s, r in ranked[:limit]]

def document_list():
    with _connect() as db:
        rows = db.execute("SELECT filename, COUNT(*) chunks FROM chunks GROUP BY filename").fetchall()
    return [dict(r) for r in rows]
