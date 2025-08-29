# python/routers/images.py
from typing import List, Optional
from pathlib import Path
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, Query, status
from models.image import UploadResp, ListImagesResp, AnalyzeReq, AnalyzeResp, ImageItem
from models.user import User
from jwt import verify_token
from utils.file import save_upload_file, UPLOAD_ROOT
from dao import image_dao
from core.model_client import analyze_images

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
    last_key: Optional[str] = Query(None, description="JSON string of the LastEvaluatedKey returned on the previous page (optional)"),
    current_user: User = Depends(verify_token),
):
    lek = None
    if last_key:
        import json
        try:
            lek = json.loads(last_key)
        except Exception:
            raise HTTPException(status_code=400, detail="Invalid last_key")
    items, next_key = image_dao.list_items(current_user.u_id, limit=limit, last_evaluated_key=lek)
    return ListImagesResp(items=items, last_evaluated_key=next_key)

@router.post("/analyze", response_model=AnalyzeResp)
async def analyze(body: AnalyzeReq, current_user: User = Depends(verify_token)):
    paths: List[Path] = []
    if body.image_ids:
        for iid in body.image_ids:
            rec = image_dao.get_by_image_id(iid)
            if not rec or rec.u_id != current_user.u_id:
                raise HTTPException(status_code=404, detail=f"image not found: {iid}")
            paths.append(UPLOAD_ROOT / rec.relative_path)
    else:
        items, _ = image_dao.list_items(current_user.u_id, limit=body.limit)
        for rec in items:
            paths.append(UPLOAD_ROOT / rec.relative_path)
    result = await analyze_images(paths, topk=body.topk)
    return AnalyzeResp(result=result)
