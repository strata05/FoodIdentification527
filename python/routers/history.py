
from typing import List, Optional
from pathlib import Path
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, Query, status
from models.image import UploadResp, ListImagesResp, AnalyzeReq, AnalyzeResp, ImageItem
from models.user import User
from jwt import verify_token
from utils.file import save_upload_file, UPLOAD_ROOT
from dao import image_dao
from core.model_client import analyze_images
from models.history import NutritionHistoryItem, NutritionHistoryResp
from dao import nutrition_dao
import json
from decimal import Decimal

router = APIRouter(prefix="/history", tags=["history"])

def convert_decimal(obj):
    """convert Decimal to float"""
    if isinstance(obj, Decimal):
        return float(obj)
    if isinstance(obj, dict):
        return {k: convert_decimal(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [convert_decimal(i) for i in obj]
    return obj

@router.get("", response_model=NutritionHistoryResp)
async def get_history(
    limit: int = Query(20, ge=1, le=100),
    last_key: Optional[str] = Query(None, description="page token"),
    current_user: User = Depends(verify_token)
):

    lek = None
    if last_key:
        try:
            lek = json.loads(last_key)
        except Exception:
            raise HTTPException(status_code=400, detail="Invalid last_key format")

    try:
        # 从 nutrition_dao 获取历史记录
        nutrition_items, next_key = nutrition_dao.list_items_by_user(
            current_user.u_id, limit=limit, last_evaluated_key=lek
        )

        # 里面有些数字无法序列化，要转换一下
        next_key_clean = convert_decimal(next_key)

        # 前端封装的get()方法需要返回的结果又success字段，不然数据会跑到error里
        return NutritionHistoryResp(
            success=True,
            items=nutrition_items,
            last_evaluated_key=next_key_clean
      
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch history: {str(e)}")