from pydantic import BaseModel
from typing import Optional, List, Dict, Any

class NutritionHistoryItem(BaseModel):
    image_id: str
    label: str
    score: float
    created_at: int  # created_at 时间戳
    nutrition: Dict[str, Any]
    original_name: str
    image_url: Optional[str] = None  

class NutritionHistoryResp(BaseModel):
    success: bool = True    
    items: List[NutritionHistoryItem]
    last_evaluated_key: Optional[Dict] = None