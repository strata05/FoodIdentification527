from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
import os

from routers import router as api_router

app = FastAPI()

#

app.include_router(api_router, prefix="/api")

# Mount static files for uploaded images
if os.path.exists("uploads"):
    app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")
