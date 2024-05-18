import os
import hashlib
import uuid
from typing import Any
from boto3.session import Session
import jwt
import datetime
import logging
from django.conf import settings

def create_token(payload: dict[str, Any], timeout: int = 60*24*7):
    headers = {
        "typ": 'jwt',
        'alg': 'HS256'
    }
    payload["exp"] = datetime.datetime.now(datetime.UTC) + datetime.timedelta(minutes=timeout)
    token = jwt.encode(payload=payload, key=settings.SALT, algorithm="HS256", headers=headers)

    return token

def upload_image(new_name, avatar_file):
    try:
        s3 = Session(
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID, 
            aws_secret_access_key=settings.AWS_ACCESS_SECRET_KEY,
            region_name=settings.REGION_NAME
        ).resource("s3")
        result = s3.Bucket(settings.BUCKET_NAME).put_object(Key=new_name, Body=avatar_file.read())
        return bool(result)
    except Exception as e:
        logging.error(e)
        return False

def get_random_str():
    """
    return random hex string
    """
    uuid_val = uuid.uuid4()
    uuid_str = str(uuid_val).encode('utf-8')
    md5 = hashlib.md5()
    md5.update(uuid_str)
    return md5.hexdigest()
