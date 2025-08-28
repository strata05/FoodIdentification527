from pydantic import BaseModel
from typing import Optional, List, Dict, Any


class ImageItem(BaseModel):
    """Image item metadata"""

    u_id: str
    image_id: str
    created_at: int
    original_name: str
    content_type: str
    size: int
    relative_path: str


class UploadResp(BaseModel):
    """Upload API response"""

    success: bool = True
    items: List[ImageItem]


class ListImagesResp(BaseModel):
    """List images response"""

    success: bool = True
    items: List[ImageItem]
    last_evaluated_key: Optional[dict] = None


class AnalyzeReq(BaseModel):
    """Analysis request"""

    image_ids: Optional[List[str]] = None
    limit: int = 10
    topk: int = 3


class AnalyzeResp(BaseModel):
    """Analysis response"""

    success: bool = True
    result: Dict[str, Any]
