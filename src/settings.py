from pathlib import Path

class Settings:
    # Base data directory
    DATA_DIR = Path("data")

    # Database file
    DB_PATH = DATA_DIR / "app.db"

    # Embeddings model
    MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

    # ChromaDB persistent directory
    CHROMA_DIR = DATA_DIR / "chroma"

settings = Settings()
