from fastapi import APIRouter
from . import user
from . import images
from . import nutrition_api
from . import debug_db            # new

router = APIRouter()
router.include_router(user.router, prefix="/user", tags=["user"])
router.include_router(images.router)
router.include_router(nutrition_api.router)
router.include_router(debug_db.router)      # new
