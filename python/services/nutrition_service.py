from __future__ import annotations
from typing import List, Dict, Any, Optional, Tuple
from dao import nutrition_dao

def _choose_label(topk: List[Dict[str, Any]]) -> Optional[Tuple[str, float]]:
    if not topk:
        return None
    best = max(topk, key=lambda x: float(x.get("score", 0)))
    return best.get("class") or best.get("label"), float(best.get("score", 0))

def _fetch_nutrition(label: str) -> Dict[str, Any]:
    from routers.nutrition import fetch_nutrition
    return fetch_nutrition(label)

def enrich_and_save_for_one(u_id: str, image_id: str,
                            topk: List[Dict[str, Any]],
                            created_at: Optional[int] = None) -> Optional[Dict[str, Any]]:
    pick = _choose_label(topk)
    if not pick:
        return None
    label, score = pick
    nutr = _fetch_nutrition(label) or {}
    item = nutrition_dao.new_item(
        u_id=u_id, image_id=image_id,
        label=label, score=score, topk=topk,
        nutrition=nutr, created_at=created_at
    )
    nutrition_dao.put_item(item)
    return item
