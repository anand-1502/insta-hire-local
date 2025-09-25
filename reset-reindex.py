from src.db import DB
from src.embeddings import EmbeddingIndex

db = DB()
idx = EmbeddingIndex()

# Drop and recreate the collection to remove old auto IDs
idx.client.delete_collection("resumes")
idx.collection = idx.client.get_or_create_collection("resumes")

cands = db.get_all_candidates()
print(f"Reindexing {len(cands)} candidates...")

for c in cands:
    text = (c.get("resume_excerpt") or "").strip()
    if not text:
        print(f"Skipping {c['name']} (no resume text)")
        continue
    idx.add_text(text, candidate_id=c["id"])
    # keep embedding_id == candidate id
    db.update_candidate_embedding(c["id"], c["id"])

print("Done.")
