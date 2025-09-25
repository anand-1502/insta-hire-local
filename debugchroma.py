from src.embeddings import EmbeddingIndex

index = EmbeddingIndex()
print("Chroma count:", index.collection.count())
print("All IDs:", index.collection.get()["ids"])
