from dataclasses import dataclass, field, fields, is_dataclass
from typing import Any, Literal, Optional
import boto3
from boto3.dynamodb.conditions import Key, Attr
import os
from uuid import uuid4
import logging

logger = logging.getLogger(__name__)

class DB:
    def __init__(self):
        region = os.environ.get('AWS_REGION', "us-east-1")


        self.db: Any = boto3.resource("dynamodb", region_name = region)
        self.table_name = os.getenv("LEAN_CHAT_TABLE_NAME", "lean-chat")
        self.table = self.db.Table(self.table_name)

    def put(self, obj):
        def to_field(v):
            t = type(v)
            if t is not str:
                print('warning: check how dynamo expects non-string values')
            return v
        if is_dataclass(obj):
            item = {f.name: to_field(getattr(obj, f.name)) for f in fields(obj)}
        elif isinstance(obj, dict):
            item = {k: to_field(v) for k,v in obj.items()}
            print(item)
        else:
            raise TypeError(f"unsupported type {type(obj)}")
        try:
            self.table.put_item(Item=item )
            return True
        except Exception as e:
            logger.error(f"Database error: {e}")
            return False
