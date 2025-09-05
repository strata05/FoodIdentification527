from fastapi import APIRouter, Depends
from jwt import verify_token               
import os, boto3
from dao import nutrition_dao               

router = APIRouter(prefix="/debug", tags=["debug"])

@router.get("/ddb")
async def ddb_overview(current_user = Depends(verify_token)):
    ep = nutrition_dao.ENDPOINT
    cli = boto3.client(
        "dynamodb",
        endpoint_url=ep,
        region_name="us-east-1",
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID", "x"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY", "x"),
    )
    tabs = cli.list_tables().get("TableNames", [])
    out = {"endpoint": ep, "tables": tabs}
    if nutrition_dao.TABLE in tabs:
        out["image_nutrition"] = cli.describe_table(TableName=nutrition_dao.TABLE)["Table"]
    return out
