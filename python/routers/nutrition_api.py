from __future__ import annotations
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from models.user import User
from jwt import verify_token
from dao import image_dao
from services.nutrition_service import enrich_and_save_for_one

router = APIRouter(prefix="/nutrition", tags=["nutrition"])

class TopK(BaseModel):
    class_: str = Field(..., alias="class")
    score: float

class OneResult(BaseModel):
    file: Optional[str] = None
    topk: List[TopK]

class SaveReq(BaseModel):
    image_ids: List[str]
    result: List[OneResult]

@router.post("/enrich_and_save")
async def enrich_and_save(req: SaveReq, current_user: User = Depends(verify_token)):
    if len(req.image_ids) != len(req.result):
        raise HTTPException(status_code=400, detail="image_ids and result length mismatch")

    saved = 0
    for iid, res in zip(req.image_ids, req.result):
        rec = image_dao.get_by_image_id(iid)
        if not rec or rec.u_id != current_user.u_id:
            raise HTTPException(status_code=404, detail=f"image not found: {iid}")
        topk = [r.dict(by_alias=True) for r in res.topk]
        ok = enrich_and_save_for_one(
            u_id=current_user.u_id,
            image_id=rec.image_id,
            topk=topk,
            created_at=rec.created_at,
        )
        if ok:
            saved += 1

    return {"ok": True, "saved": saved}
