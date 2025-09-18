from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from dotenv import load_dotenv
import boto3
import sys
import os

from routers import router as api_router
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "..", ".env"))
print("DEBUG S3_BUCKET =", os.getenv("S3_BUCKET"), flush=True)
print("DEBUG DDB_TABLE_USERS =", os.getenv("DDB_TABLE_USERS"), flush=True)
print("DEBUG DDB_TABLE_USER_IMAGES =", os.getenv("DDB_TABLE_USER_IMAGES"), flush=True)
sys.stdout.flush()
try:
    ddb = boto3.client("dynamodb", region_name=os.getenv("AWS_REGION"))
    tables = ddb.list_tables()
    print("DEBUG DynamoDB tables =", tables, flush=True)
except Exception as e:
    print("DEBUG DynamoDB error =", e, flush=True)
app = FastAPI()


ALLOWED_ORIGINS = [
    "http://127.0.0.1:5173",
    "http://localhost:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "Accept", "Origin", "X-Requested-With"],
    expose_headers=["*"],
    max_age=86400,
)

app.include_router(api_router, prefix="/api")


if os.path.exists("uploads"):
    app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")
