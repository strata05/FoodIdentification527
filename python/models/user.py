from typing import Optional

from pydantic import BaseModel


class User(BaseModel):
    u_id: str = None
    email: str
    password: str
    avatar: Optional[str] = ''
    username: str
    created_at: int
    updated_at: int
