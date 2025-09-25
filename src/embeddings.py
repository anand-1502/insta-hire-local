import json
from typing import List, Tuple
import numpy as np
from sentence_transformers import SentenceTransformer
import chromadb
from chromadb.config import Settings as ChromaSettings
from src.settings import settings

class EmbeddingIndex:
    def __init__(self):
        self.model = SentenceTransformer(settings.MODEL_NAME)
        self.chroma_client = chromadb.PersistentClient(path=str(settings.CHROMA_DIR))
        self.collection = self.chroma_client.get_or_create_collection(
            name="resumes", metadata={"hnsw:space": "cosine"}
        )

    def embed(self, text: str) -> List[float]:
        return self.model.encode([text], normalize_embeddings=True)[0].tolist()

    def add_text(self, text: str) -> int:
        emb = self.embed(text)
        # Generate ID
        next_id = str(len(self.collection.get()["ids"]) + 1)
        self.collection.add(documents=[text], embeddings=[emb], ids=[next_id])
        return int(next_id)

    def search(self, query_text: str, k: int = 50) -> Tuple[List[int], List[float]]:
        if len(self.collection.get()["ids"]) == 0:
            return [], []
        qv = self.embed(query_text)
        res = self.collection.query(query_embeddings=[qv], n_results=k)
        ids = [int(i) for i in res["ids"][0]]
        scores = res["distances"][0]
        return ids, scores

    def add_text(self, text: str, candidate_id: int) -> str:
        cid = str(candidate_id)
        self.collection.add(documents=[text], ids=[cid], metadatas=[{"candidate_id": candidate_id}])
        return cid

