from __future__ import annotations
from typing import Dict, Any, List, Optional
import time, os, boto3
from decimal import Decimal
from botocore.exceptions import ClientError
from boto3.dynamodb.conditions import Key
from models.history import NutritionHistoryItem
from botocore.exceptions import ClientError
from .image_dao import get_by_image_id

TABLE = os.getenv("NUTRITION_TABLE", "image_nutrition")
# NEW: support both env names and default to 8011
ENDPOINT = (
    os.getenv("DYNAMODB_ENDPOINT")
    or os.getenv("DYNAMO_ENDPOINT")
    or "http://127.0.0.1:8011"
)
REGION = os.getenv("AWS_REGION", "us-east-1")

_dynamo = boto3.resource(
    "dynamodb",
    endpoint_url=ENDPOINT,
    region_name=REGION,
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID", "dummy"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY", "dummy"),
)

def _wait_table_active(cli, table: str) -> None:
    for _ in range(120):
        st = cli.describe_table(TableName=table)["Table"]["TableStatus"]
        if st == "ACTIVE":
            return
        time.sleep(0.5)
    raise TimeoutError(f"Table {table} not ACTIVE")

def _gsi_exists(desc: dict, name: str) -> bool:
    return any(i["IndexName"] == name for i in desc.get("GlobalSecondaryIndexes", []))

def ensure_table() -> None:
    cli = _dynamo.meta.client
    try:
        _dynamo.Table(TABLE).load()
    except ClientError as e:
        if e.response.get("Error", {}).get("Code") != "ResourceNotFoundException":
            raise
        _dynamo.create_table(
            TableName=TABLE,
            KeySchema=[
                {"AttributeName": "u_id", "KeyType": "HASH"},
                {"AttributeName": "created_at", "KeyType": "RANGE"},
            ],
            AttributeDefinitions=[
                {"AttributeName": "u_id", "AttributeType": "S"},
                {"AttributeName": "created_at", "AttributeType": "N"},
                {"AttributeName": "image_id", "AttributeType": "S"},
            ],
            GlobalSecondaryIndexes=[
                {
                    "IndexName": "imageIdIndex",
                    "KeySchema": [{"AttributeName": "image_id", "KeyType": "HASH"}],
                    "Projection": {"ProjectionType": "ALL"},
                }
            ],
            BillingMode="PAY_PER_REQUEST",
        ).wait_until_exists()

    # NEW: ensure GSI exists even if table was created before without it
    desc = cli.describe_table(TableName=TABLE)["Table"]
    if not _gsi_exists(desc, "imageIdIndex"):
        cli.update_table(
            TableName=TABLE,
            AttributeDefinitions=[{"AttributeName": "image_id", "AttributeType": "S"}],
            GlobalSecondaryIndexUpdates=[
                {
                    "Create": {
                        "IndexName": "imageIdIndex",
                        "KeySchema": [{"AttributeName": "image_id", "KeyType": "HASH"}],
                        "Projection": {"ProjectionType": "ALL"},
                        # DynamoDB Local accepts this; fine for local usage
                        "ProvisionedThroughput": {"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
                    }
                }
            ],
        )
        _wait_table_active(cli, TABLE)

def new_item(
    u_id: str,
    image_id: str,
    label: str,
    score: float,
    topk: List[Dict[str, Any]],
    nutrition: Dict[str, Any],
    created_at: Optional[int] = None,
) -> Dict[str, Any]:
    now_ms = int(time.time() * 1000) if created_at is None else int(created_at)
    return {
        "u_id": u_id,
        "created_at": now_ms,
        "image_id": image_id,
        "label": label,
        "score": float(score),
        "topk": topk,
        "nutrition": nutrition,
        "source": nutrition.get("source") if nutrition else None,
    }

def _decimalize(value: Any) -> Any:
    if isinstance(value, float):
        return Decimal(str(value))
    if isinstance(value, list):
        return [_decimalize(v) for v in value]
    if isinstance(value, dict):
        return {k: _decimalize(v) for k, v in value.items()}
    return value

def put_item(item: Dict[str, Any]) -> None:
    ensure_table()
    item = _decimalize(item)
    _dynamo.Table(TABLE).put_item(Item=item)



_table = None

def _get():
    global _table
    if _table:
        return _table
    _table = _dynamo.Table(TABLE)  
    try:
        _table.load()
        return _table
    except ClientError as e:
        if e.response.get("Error", {}).get("Code") == "ResourceNotFoundException":
            ensure_table() 
            return _get()  
        raise


def list_items_by_user(u_id: str, limit: int = 20, last_evaluated_key: Optional[dict] = None):
    kwargs = {
        "KeyConditionExpression": Key("u_id").eq(u_id),
        "ScanIndexForward": False,  
        "Limit": limit,
    }

    if last_evaluated_key:
        kwargs["ExclusiveStartKey"] = last_evaluated_key
        
    resp = _get().query(**kwargs)

    items = []
    for raw in resp.get("Items", []):
        url = get_by_image_id(raw["image_id"]).relative_path

  
        name = raw.get("original_name", "")
        if isinstance(name, dict):
            name = name.get("filename") or "unknown"

        items.append(NutritionHistoryItem(
            image_id=str(raw["image_id"]),
            label=str(raw["label"]),
            score=float(raw["score"]),
            created_at=int(raw["created_at"]),
            nutrition=dict(raw["nutrition"]),
            original_name=name,
            image_url=url
        ))
 

    return items, resp.get("LastEvaluatedKey")

