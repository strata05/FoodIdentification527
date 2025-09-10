# routers/images.py
from typing import List, Optional
import time, json
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, Query, status
from models.image import ImageItem, AnalyzeReq, AnalyzeResp  # 仍保留你的模型
from models.user import User
from jwt import verify_token
from dao import image_dao
from core.model_client import analyze_images
from utils.s3_utils import upload_fileobj, presign_get

router = APIRouter(prefix="/images", tags=["images"])


@router.post("/upload", status_code=status.HTTP_201_CREATED)
async def upload_images(
    files: List[UploadFile] = File(..., description="support multiple files"),
    current_user: User = Depends(verify_token),
):
    """
    接收文件 -> 直接上传 S3，不再写入本地 uploads/
    在 DynamoDB(user_images) 写入元数据(relative_path= S3 Key)
    返回 items，并额外附加一个 'url' (预签名) 便于前端直接 <img src=...>
    """
    if not files:
        raise HTTPException(status_code=400, detail="No files")

    items: List[dict] = []
    for f in files:
        # 0) 获取大小（尽量）
        try:
            pos = f.file.tell()
            f.file.seek(0, 2)
            size = f.file.tell()
            f.file.seek(pos)
        except Exception:
            size = 0

        # 1) 生成 S3 key
        now_ms = int(time.time() * 1000)
        s3_key = f"user/{current_user.u_id}/{now_ms}_{f.filename}"

        # 2) 上传到 S3
        try:
            upload_fileobj(f.file, s3_key, content_type=f.content_type)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"S3 upload failed: {e}")

        # 3) 写 DynamoDB（relative_path 存 S3 Key）
        item = image_dao.new_item(
            u_id=current_user.u_id,
            relative_path=s3_key,
            original_name=f.filename or "file",
            content_type=f.content_type or "application/octet-stream",
            size=int(size or 0),
        )
        image_dao.put_item(item)

        # 4) 返回里附带预签名 URL，前端可直接显示
        items.append({**item.model_dump(), "url": presign_get(s3_key)})

    return {"items": items}


@router.get("")
async def list_my_images(
    limit: int = Query(20, ge=1, le=100),
    last_key: Optional[str] = Query(
        None,
        description="JSON string of the LastEvaluatedKey returned on the previous page (optional)",
    ),
    current_user: User = Depends(verify_token),
):
    """
    列出当前用户的图片清单，并为每条记录生成 'url' 方便前端展示
    """
    lek = None
    if last_key:
        try:
            lek = json.loads(last_key)
        except Exception:
            raise HTTPException(status_code=400, detail="Invalid last_key")

    items, next_key = image_dao.list_items(
        current_user.u_id, limit=limit, last_evaluated_key=lek
    )

    out = [{**i.model_dump(), "url": presign_get(i.relative_path)} for i in items]
    return {"items": out, "last_evaluated_key": next_key}


@router.get("/{image_id}/url")
async def get_image_url(image_id: str, current_user: User = Depends(verify_token)):
    """
    单独按 image_id 获取预签名 URL（可选，给前端懒加载用）
    """
    rec = image_dao.get_by_image_id(image_id)
    if not rec or rec.u_id != current_user.u_id:
        raise HTTPException(status_code=404, detail="image not found")
    return {"url": presign_get(rec.relative_path)}


@router.post("/analyze")
async def analyze(body: AnalyzeReq, current_user: User = Depends(verify_token)):
    """
    使用预签名 URL 作为输入进行分析
    如果 analyze_images 只能接受本地路径，再告诉我我给你换为临时下载再分析的版本
    """
    urls: List[str] = []
    if body.image_ids:
        for iid in body.image_ids:
            rec = image_dao.get_by_image_id(iid)
            if not rec or rec.u_id != current_user.u_id:
                raise HTTPException(status_code=404, detail=f"image not found: {iid}")
            urls.append(presign_get(rec.relative_path))
    else:
        items, _ = image_dao.list_items(current_user.u_id, limit=body.limit)
        for rec in items:
            urls.append(presign_get(rec.relative_path))

    result = await analyze_images(urls, topk=body.topk)
    return AnalyzeResp(result=result)
