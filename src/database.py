from dataclasses import dataclass, field, fields, is_dataclass
from typing import Any, Literal, Optional
import boto3
from boto3.dynamodb.conditions import Key, Attr
import os
from uuid import uuid4

dynamodb: Any = boto3.resource("dynamodb")
TABLE_NAME = os.getenv("LEAN_CHAT_TABLE_NAME", "lean-chat")
table = dynamodb.Table(TABLE_NAME)


def put(obj):
    assert is_dataclass(obj)

    def to_field(f):
        v = getattr(obj, f.name)
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

    dynamodb.put_item(
        TableName=TABLE_NAME, Item={f.name: to_field(f) for f in fields(obj)}
    )
