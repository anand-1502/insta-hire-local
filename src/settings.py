from pathlib import Path

class Settings:
    DATA_DIR = str(Path("data").resolve())
    DB_PATH = str(Path(DATA_DIR) / "app.db")
    FAISS_DIR = str(Path(DATA_DIR) / "faiss")
    FAISS_INDEX_PATH = str(Path(FAISS_DIR) / "index.faiss")
    ID_MAP_PATH = str(Path(FAISS_DIR) / "id_map.json")
    MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

settings = Settings()
