import boto3 # type: ignore
from botocore.client import Config # type: ignore
from boto3 import session # type: ignore

ENDPOINT_URL = 'https://c0a2708751cb7c1c812609e3cf2fb43a.r2.cloudflarestorage.com'
ACCESS_KEY = 'c4ea00439cb6bf83b8f2d29769952a4a'
SECRET_KEY = 'bf6cb738632db03d03606c1c94e18da6027eda1eeb86c38d66abaae9bcb4dc62'
BUCKET = 'quibbler'

client = session.Session().client(
    's3',
    endpoint_url=ENDPOINT_URL,
    aws_access_key_id=ACCESS_KEY,
    aws_secret_access_key=SECRET_KEY,
    config=Config(signature_version='s3v4'),
    region_name='auto'
)

def get_signed_url(filename, expires=86400):
    return client.generate_presigned_url(
        ClientMethod='get_object',
        Params={'Bucket': BUCKET, 'Key': filename},
        ExpiresIn=expires
    )
