from dataclasses import dataclass, field, fields, is_dataclass
from typing import Any, Literal, Optional
import boto3
from boto3.dynamodb.conditions import Key, Attr
import os
from uuid import uuid4
import logging

logger = logging.getLogger(__name__)

dynamodb: Any = boto3.resource("dynamodb")
TABLE_NAME = os.getenv("LEAN_CHAT_TABLE_NAME", "lean-chat")
table = dynamodb.Table(TABLE_NAME)

def put(obj):
    def to_field(k):

        v = getattr(obj, k)
        t = type(v)
        if t is str:
            return {"S": v}
        if t is bytes:
            return {"B": v}
        if isinstance(v, (int, float)):
            return {"N": str(v)}
        if t is bool:
            return {"BOOL": v}
        if v is None:
            return {"NULL": True}
        raise TypeError(f"unsupported type {t}")

    if is_dataclass(obj):
        item = {f.name: to_field(f.name) for f in fields(obj)}
    elif isinstance(obj, dict):
        item = {k: to_field(k) for k in obj.keys()}
    else:
        raise TypeError(f"unsupported type {type(obj)}")
    try:
        dynamodb.put_item(
            TableName=TABLE_NAME, Item=item
        )
        return True
    except Exception as e:
        logger.error(f"Database error: {e}")
        return False
