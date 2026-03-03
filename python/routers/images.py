from typing import List, Optional
from pathlib import Path
import inspect  # NEW: for async/sync fetch_nutrition detection
import logging  # NEW

from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, Query, status
from models.image import UploadResp, ListImagesResp, AnalyzeReq, AnalyzeResp, ImageItem
from models.user import User
from jwt import verify_token
from utils.file import save_upload_file, UPLOAD_ROOT
from dao import image_dao
from core.model_client import analyze_images

from .nutrition import fetch_nutrition  
from dao import nutrition_dao          
import inspect                         

# NEW: nutrition auto-enrich & save
from services.nutrition_service import enrich_and_save_for_one  # NEW


logger = logging.getLogger(__name__)  # NEW

router = APIRouter(prefix="/images", tags=["images"])


@router.post("/upload", response_model=UploadResp, status_code=status.HTTP_201_CREATED)
async def upload_images(
    files: List[UploadFile] = File(..., description="support multiple files"),
    current_user: User = Depends(verify_token),
):
    if not files:
        raise HTTPException(status_code=400, detail="No files")
    items: List[ImageItem] = []
    for f in files:
        rel, size, ctype = save_upload_file(current_user.u_id, f)
        item = image_dao.new_item(
            u_id=current_user.u_id,
            relative_path=rel,
            original_name=f.filename or "file",
            content_type=ctype,
            size=size,
        )
        image_dao.put_item(item)
        items.append(item)
    return UploadResp(items=items)


@router.get("", response_model=ListImagesResp)
async def list_my_images(
    limit: int = Query(20, ge=1, le=100),
    last_key: Optional[str] = Query(
        None,
        description="JSON string of the LastEvaluatedKey returned on the previous page (optional)",
    ),
    current_user: User = Depends(verify_token),
):
    lek = None
    if last_key:
        import json

        try:
            lek = json.loads(last_key)
        except Exception:
            raise HTTPException(status_code=400, detail="Invalid last_key")
    items, next_key = image_dao.list_items(
        current_user.u_id, limit=limit, last_evaluated_key=lek
    )
    return ListImagesResp(items=items, last_evaluated_key=next_key)


@router.post("/analyze", response_model=AnalyzeResp)
async def analyze(body: AnalyzeReq, current_user: User = Depends(verify_token)):
    paths: List[Path] = []
    recs: List[ImageItem] = []  # NEW: keep records to know image_id for saving

    if body.image_ids:
        for iid in body.image_ids:
            rec = image_dao.get_by_image_id(iid)
            if not rec or rec.u_id != current_user.u_id:
                raise HTTPException(status_code=404, detail=f"image not found: {iid}")
            paths.append(UPLOAD_ROOT / rec.relative_path)
            recs.append(rec)  # NEW
    else:
        items, _ = image_dao.list_items(current_user.u_id, limit=body.limit)
        for rec in items:
            paths.append(UPLOAD_ROOT / rec.relative_path)
            recs.append(rec)  # NEW

    raw = await analyze_images(paths, topk=body.topk)
    print(f"Raw analysis result: {raw}")
    print(f"Raw result type: {type(raw)}")

    # NEW: normalize various shapes into a list of dicts with "topk"
    if isinstance(raw, dict) and "results" in raw:
        seq = raw["results"]
    else:
        seq = raw

    def _to_dict(x):
        # NEW: make pydantic/dataclass/dict -> dict
        if isinstance(x, dict):
            return x
        md = getattr(x, "model_dump", None)
        if callable(md):
            return md()
        d = getattr(x, "dict", None)
        if callable(d):
            return d()
        return None

    norm: List[dict] = []
    for item in seq or []:
        if isinstance(item, str):
            norm.append({"file": item, "topk": []})
            continue
        item = _to_dict(item)
        if not isinstance(item, dict):
            continue

        topk = item.get("topk") or []
        fixed_topk: List[dict] = []
        for t in topk:
            if isinstance(t, dict):
                label = t.get("class") or t.get("label") or t.get("name")
                sc = t.get("score") or t.get("prob") or 0
            elif isinstance(t, (list, tuple)) and len(t) >= 2:
                label, sc = t[0], t[1]
            else:
                continue
            try:
                sc = float(sc)
            except Exception:
                sc = 0.0
            fixed_topk.append(
                {"class": str(label) if label is not None else "", "score": sc}
            )

        item["topk"] = fixed_topk
        norm.append(item)

    # NEW: auto-enrich & save top-1 prediction for each image; never break analyze() if it fails
    try:
        for rec, item in zip(recs, norm):
            top1 = (item.get("topk") or [None])[0]
            item["image_id"] = rec.image_id              
            item["original_name"] = getattr(rec, "original_name", "")  
            if not top1 or not top1.get("class"):
                continue
            label = top1["class"]
            score = float(top1.get("score") or 0)

            if inspect.iscoroutinefunction(fetch_nutrition):
                nutrition = await fetch_nutrition(label)
            else:
                nutrition = fetch_nutrition(label)

            nutrition_dao.put_item(
                nutrition_dao.new_item(
                    u_id=current_user.u_id,
                    image_id=rec.image_id,
                    label=label,
                    score=score,
                    topk=item.get("topk") or [],
                    nutrition=nutrition,
                )
            )
    except Exception as e:
        logger.exception("auto enrich/save failed: %s", e)  # NEW

    # FIX: AnalyzeResp.result must be a dict, not a list
    resp_result = {"mock": False, "success": True, "results": norm}  # FIX
    return AnalyzeResp(result=resp_result)  # FIX
