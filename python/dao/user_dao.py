from botocore.exceptions import ClientError
import boto3
from boto3.dynamodb.conditions import Key

from db import dynamodb
from models.user import User

table_name = "users"
table = None

def __create_user_table():
    global table
    table = dynamodb.create_table(
        TableName=table_name,
        KeySchema=[
            {'AttributeName': 'u_id', 'KeyType': 'HASH'},
            {"AttributeName": "created_at", "KeyType": "RANGE"}
        ],
        AttributeDefinitions=[
            {'AttributeName': 'u_id', 'AttributeType': 'S'},
            {"AttributeName": "created_at", "AttributeType": "N"},
            {"AttributeName": "email", "AttributeType": "S"}
        ],
        GlobalSecondaryIndexes=[
            {
                "IndexName": "emailIndex",
                "KeySchema": [{"AttributeName": "email", "KeyType": "HASH"}],
                "Projection": {
                    "ProjectionType": "ALL"
                },
                "ProvisionedThroughput": {"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
            }
        ],
        ProvisionedThroughput={'ReadCapacityUnits': 5, 'WriteCapacityUnits': 5}
    )
    # waiting create table finished
    table.meta.client.get_waiter('table_exists').wait(TableName=table_name)
    return table

def create_user_table():
    global table
    table = dynamodb.Table(table_name)
    try:
        table.load()
        return table
    except ClientError as e:
        if e.response['Error']['Code'] == 'ResourceNotFoundException':
            return __create_user_table()
        else:
            raise

def get_table():
    """

    :return:
    """
    global table
    if table is None:
        return create_user_table()
    return table

def find_user_by_email(email: str):
    """
    :param email:
    :return:
    """
    _table = get_table()
    resp = _table.query(
        IndexName="emailIndex",
        KeyConditionExpression=Key("email").eq(email),
        Limit=1
    )
    items = resp["Items"]
    if len(items) == 0:
        return None

    result = User(**items[0])
    return result

def insert_user(user: User):
    """
    :param user:
    :return:
    """
    _table = get_table()
    print(user.model_dump())
    _table.put_item(Item=user.model_dump())

def find_user_by_id(user_id: str):
    """
    :param user_id:
    :return:
    """
    _table = get_table()
    resp = _table.query(KeyConditionExpression=Key("u_id").eq(user_id), Limit=1)

    items = resp["Items"]
    if len(items) == 0:
        return None

    result = User(**items[0])
    return result


