from src.db import DB

db = DB()
all_cands = db.get_all_candidates()
print(f"Found {len(all_cands)} candidates")

for c in all_cands:
    db.update_candidate_embedding(c["id"], c["id"])
    print(f"Synced {c['name']} -> embedding_id {c['id']}")
