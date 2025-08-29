from fastapi import APIRouter
from . import user
from . import images

router = APIRouter()
router.include_router(user.router, prefix="/user", tags=["user"])
router.include_router(images.router)