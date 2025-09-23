import datetime
import os

from botocore.signers import CloudFrontSigner
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import padding

import boto3
from botocore.exceptions import ClientError
from functools import lru_cache


CF_KEY_PAIR_ID = os.getenv("CF_KEY_PAIR_ID", "K2GVWXDCGY0O66")
CF_DIST_DOMAIN = os.getenv("CF_DIST_DOMAIN", "food.x0yz.xyz")
SECRET_ID = os.getenv("CF_PRIVATE_KEY_SECRET_ID", "cf/signer/private-key")


REGION_NAME = "us-east-1"


@lru_cache(maxsize=3)
def get_secret(secret_id:str):
    # Create a Secrets Manager client
    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name=REGION_NAME
    )

    try:
        get_secret_value_response = client.get_secret_value(
            SecretId=secret_id
        )
    except ClientError as e:
        raise e

    return get_secret_value_response['SecretString']


#
PRIVATE_KEY = get_secret(SECRET_ID).encode("utf-8")

def rsa_sha1_signer(message: bytes) -> bytes:
    key = serialization.load_pem_private_key(PRIVATE_KEY, password=None, backend=default_backend())
    return key.sign(message, padding.PKCS1v15(), hashes.SHA1())

def sign_url_canned(object_key: str, expires_in_seconds: int = 600) -> str:
    url = f"https://{CF_DIST_DOMAIN}/{object_key}"
    expire_at = datetime.datetime.utcnow() + datetime.timedelta(seconds=expires_in_seconds)
    signer = CloudFrontSigner(CF_KEY_PAIR_ID, rsa_sha1_signer)
    return signer.generate_presigned_url(url, date_less_than=expire_at)

