from src.db import DB
from src.embeddings import EmbeddingIndex

db = DB()
index = EmbeddingIndex()

all_candidates = db.get_all_candidates()
print(f"Found {len(all_candidates)} candidates in DB")

for cand in all_candidates:
    # Skip if already has embedding
    if cand.get("embedding_id"):
        continue

    resume_text = cand.get("resume_excerpt") or ""
    if not resume_text.strip():
        print(f"⚠️ Skipping {cand['name']} (no resume text)")
        continue

    emb_id = index.add_text(resume_text)
    db.update_candidate_embedding(cand["id"], emb_id)
    print(f"✅ Reindexed {cand['name']} with embedding id {emb_id}")

print("Done! Candidates are now in Chroma.")
