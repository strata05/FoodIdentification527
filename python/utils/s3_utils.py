import boto3

BUCKET = "food-identification-images"   # 换成你的桶名
REGION = "us-east-1"

s3 = boto3.client("s3", region_name=REGION)

def upload_fileobj(fileobj, key: str, content_type: str = None):
    extra = {"ServerSideEncryption": "AES256"}
    if content_type:
        extra["ContentType"] = content_type
    s3.upload_fileobj(fileobj, BUCKET, key, ExtraArgs=extra)

def presign_get(key: str, expires: int = 3600) -> str:
    return s3.generate_presigned_url(
        "get_object",
        Params={"Bucket": BUCKET, "Key": key},
        ExpiresIn=expires,
    )
