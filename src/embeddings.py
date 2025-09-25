import json
from pathlib import Path
from typing import List, Tuple
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
from src.settings import settings

class EmbeddingIndex:
    def __init__(self):
        Path(settings.FAISS_DIR).mkdir(parents=True, exist_ok=True)
        self.model = SentenceTransformer(settings.MODEL_NAME)
        self.d = self.model.get_sentence_embedding_dimension()
        self.index_path = Path(settings.FAISS_INDEX_PATH)
        self.id_map_path = Path(settings.ID_MAP_PATH)
        self.index = self._load_or_create_index()
        self.id_map = self._load_or_create_id_map()

    def _load_or_create_index(self):
        if self.index_path.exists():
            return faiss.read_index(str(self.index_path))
        return faiss.IndexFlatL2(self.d)

    def _load_or_create_id_map(self):
        if self.id_map_path.exists():
            return json.loads(self.id_map_path.read_text())
        return {"next_id": 0}

    def _persist(self):
        faiss.write_index(self.index, str(self.index_path))
        self.id_map_path.write_text(json.dumps(self.id_map))

    def embed(self, text: str) -> np.ndarray:
        vec = self.model.encode([text], convert_to_numpy=True, normalize_embeddings=True)
        return vec.astype("float32")

    def add_text(self, text: str) -> int:
        vec = self.embed(text)
        emb_id = int(self.id_map["next_id"])
        self.index.add(vec)
        self.id_map["next_id"] = emb_id + 1
        self._persist()
        return emb_id

    def search(self, query_text: str, k: int = 50) -> Tuple[List[int], List[float]]:
        if self.index.ntotal == 0:
            return [], []
        qv = self.embed(query_text)
        distances, idxs = self.index.search(qv, min(k, self.index.ntotal))
        # Because we do not store per-vector IDs in a separate mapping, we map FAISS row index to our emb_id = row_id
        # For IndexFlatL2 with only adds, FAISS row index is the same as insertion order
        ids = idxs[0].tolist()
        dists = distances[0].tolist()
        return ids, dists
