import time
from typing import Optional, List, Tuple, Dict, Any
from boto3.dynamodb.conditions import Key
from botocore.exceptions import ClientError
from db import dynamodb
from models.image import ImageItem

"""
DAO (Data Access Object) for the DynamoDB `user_images` table.

- Lazily loads and caches the table object; creates it automatically if missing.
- Schema: primary key u_id (HASH, S) + created_at (RANGE, N); GSI imageIdIndex (image_id, S).
- Methods:
  * put_item(ImageItem): write a single record
  * list_items(u_id, limit, last_key): paginated query in reverse chronological order
  * get_by_image_id(image_id): exact lookup via the GSI
  * new_item(...): construct an ImageItem (with millisecond timestamp)
"""


TABLE = "user_images"
_table = None


def _create():
    global _table
    _table = dynamodb.create_table(
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
                "ProvisionedThroughput": {
                    "ReadCapacityUnits": 5,
                    "WriteCapacityUnits": 5,
                },
            }
        ],
        ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
    )
    _table.wait_until_exists()
    return _table


def _get():
    global _table
    if _table:
        return _table
    _table = dynamodb.Table(TABLE)
    try:
        _table.load()
        return _table
    except ClientError as e:
        if e.response["Error"]["Code"] == "ResourceNotFoundException":
            return _create()
        raise


def put_item(item: ImageItem):
    _get().put_item(Item=item.model_dump())


def list_items(
    u_id: str, limit: int = 20, last_evaluated_key: Optional[dict] = None
) -> Tuple[List[ImageItem], Optional[dict]]:
    kwargs: Dict[str, Any] = {
        "KeyConditionExpression": Key("u_id").eq(u_id),
        "ScanIndexForward": False,
        "Limit": limit,
    }
    if last_evaluated_key:
        kwargs["ExclusiveStartKey"] = last_evaluated_key
    resp = _get().query(**kwargs)
    items = [ImageItem(**i) for i in resp.get("Items", [])]
    return items, resp.get("LastEvaluatedKey")


def get_by_image_id(image_id: str) -> Optional[ImageItem]:
    resp = _get().query(
        IndexName="imageIdIndex",
        KeyConditionExpression=Key("image_id").eq(image_id),
        Limit=1,
    )
    it = resp.get("Items", [])
    return ImageItem(**it[0]) if it else None


def new_item(
    u_id: str, relative_path: str, original_name: str, content_type: str, size: int
) -> ImageItem:
    now_ms = int(time.time() * 1000)  # millisecond timestamp
    return ImageItem(
        u_id=u_id,
        image_id=f"{now_ms}_{original_name}",  # e.g. "1753725605123_pizza.png"
        created_at=now_ms,  # e.g. 1753725605123
        original_name=original_name,
        content_type=content_type,
        size=size,
        relative_path=relative_path,
    )
