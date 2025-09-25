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
    if req_days and not (cand_days.intersection(set(req_days))):
        return False
    if req_times and not (cand_times.intersection(set(req_times))):
        return False
    return True


import json

def filter_and_rank(
    job_text: str,
    candidates: list[dict],
    req_city: str,
    req_state: str,
    req_days: list[str],
    req_times: list[str],
    pay_min: float,
    pay_max: float,
    id_rank: list[int],
    id_scores: list[float],
) -> list[dict]:
    rank_map = {int(emb_id): i for i, emb_id in enumerate(id_rank)}
    score_map = {int(emb_id): s for emb_id, s in zip(id_rank, id_scores)}

    best = []
    for c in candidates:
        emb_id = int(c.get("id", -1))
        if emb_id not in rank_map:
            continue

        # Base score from vector search (lower distance = closer match)
        score = -score_map.get(emb_id, 0.0)

        # Boost if location matches
        if req_city and req_city.strip().lower() == (c.get("city") or "").lower():
            score += 1.0
        if req_state and req_state.strip().lower() == (c.get("state") or "").lower():
            score += 0.5

        # Boost if pay overlaps
        try:
            cmin = float(c.get("pay_min") or 0)
            cmax = float(c.get("pay_max") or 0)
            if (pay_min <= cmax) and (pay_max >= cmin):
                score += 1.0
        except Exception:
            pass

        # Boost if availability overlaps
        try:
            avail = json.loads(c.get("availability") or "{}")
            cand_days = set(avail.get("days", []))
            cand_times = set(avail.get("times", []))
            if req_days and cand_days.intersection(set(req_days)):
                score += 0.5
            if req_times and cand_times.intersection(set(req_times)):
                score += 0.5
        except Exception:
            pass

        c["_final_score"] = score
        best.append(c)

    # Sort by score (higher = better)
    best.sort(key=lambda x: x["_final_score"], reverse=True)
    return best
