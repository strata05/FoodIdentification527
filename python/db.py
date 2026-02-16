import os
import boto3

env = os.getenv("ENV", "development")


if env == "production":
    dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
else:
    ENDPOINT = (
        os.getenv("DYNAMODB_ENDPOINT")
        or os.getenv("DYNAMO_ENDPOINT")
        or "http://localhost:8011"
    )

    dynamodb = boto3.resource(
        "dynamodb",
        endpoint_url=ENDPOINT,
        region_name="us-east-1",
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID", "fakeMyKeyId"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY", "fakeSecretAccessKey"),
    )
