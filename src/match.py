import json
from typing import List, Dict, Any

def _city_state_match(c: Dict[str, Any], req_city: str, req_state: str) -> bool:
    if not req_city and not req_state:
        return True
    cand_city = (c.get("city") or "").strip().lower()
    cand_state = (c.get("state") or "").strip().lower()
    ok_city = True if not req_city else (req_city.strip().lower() == cand_city)
    ok_state = True if not req_state else (req_state.strip().lower() == cand_state)
    return ok_city and ok_state

def _pay_overlap(c: Dict[str, Any], pay_min: float, pay_max: float) -> bool:
    try:
        cmin = float(c.get("pay_min") or 0)
        cmax = float(c.get("pay_max") or 0)
    except Exception:
        return True
    if pay_min > 0 and cmax < pay_min:
        return False
    if pay_max > 0 and cmin > pay_max:
        return False
    return True

def _availability_overlap(c: Dict[str, Any], req_days: List[str], req_times: List[str]) -> bool:
    if not req_days and not req_times:
        return True
    avail = {"days": [], "times": []}
    if c.get("availability"):
        try:
            avail = json.loads(c["availability"])
        except Exception:
            pass
    cand_days = set(avail.get("days", []))
    cand_times = set(avail.get("times", []))
    # Require at least one overlap on days and times if provided
    if req_days and not (cand_days.intersection(set(req_days))):
        return False
    if req_times and not (cand_times.intersection(set(req_times))):
        return False
    return True

def filter_and_rank(
    job_text: str,
    candidates: List[Dict[str, Any]],
    req_city: str,
    req_state: str,
    req_days: List[str],
    req_times: List[str],
    pay_min: float,
    pay_max: float,
    id_rank: List[int],
    id_scores: List[float],
) -> List[Dict[str, Any]]:
    # Create a quick rank map from FAISS search
    rank_map = {emb_id: i for i, emb_id in enumerate(id_rank)}
    score_map = {emb_id: s for emb_id, s in zip(id_rank, id_scores)}
    # Lower distance is better for L2
    best = []
    for c in candidates:
        if not _city_state_match(c, req_city, req_state):
            continue
        if not _pay_overlap(c, pay_min, pay_max):
            continue
        if not _availability_overlap(c, req_days, req_times):
            continue
        emb_id = int(c.get("embedding_id", -1))
        # Keep only results that came from FAISS
        if emb_id not in rank_map:
            continue
        c["_faiss_rank"] = rank_map[emb_id]
        c["_faiss_score"] = score_map.get(emb_id, 0.0)
        best.append(c)

    # Rank by FAISS order first, then simple pay proximity to mid range
    mid = (pay_min + pay_max) / 2.0 if (pay_min and pay_max and pay_max > pay_min) else pay_max or pay_min or 0
    def _pay_gap(c):
        try:
            cmin = float(c.get("pay_min") or 0)
            cmax = float(c.get("pay_max") or 0)
            c_mid = (cmin + cmax) / 2.0
            return abs(c_mid - mid)
        except Exception:
            return 1e9

    best.sort(key=lambda x: (x["_faiss_rank"], _pay_gap(x)))
    return best
