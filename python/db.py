import boto3
#
dynamodb = boto3.resource(
    'dynamodb',
    endpoint_url="http://localhost:8011",
    region_name="us-east-1",
    aws_access_key_id="fakeMyKeyId",
    aws_secret_access_key="fakeSecretAccessKey"
)

