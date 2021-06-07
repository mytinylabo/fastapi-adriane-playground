import logging
from datetime import datetime
from mongoengine import connect
from mongoengine.document import Document
from mongoengine import ValidationError
from mongoengine.fields import IntField, StringField, ListField, DateTimeField, UUIDField

from uuid import uuid4

logging.basicConfig(level=logging.DEBUG)


def node_id(node_type):
    return lambda: f"{node_type}:{str(uuid4())}"


def fixed_length(n):
    def validate(seq):
        if len(seq) != n:
            raise ValidationError(
                f"len({seq}) should be {n}, but is {len(seq)}")
    return validate


class RunnerDef(Document):
    uid = StringField(primary_key=True, default=node_id("RunnerDef"))
    name = StringField(required=True)
    variant = StringField(required=True)
    unique_skills = ListField(StringField(), required=True)
    created_at = DateTimeField(default=lambda: datetime.utcnow())


class Runner(Document):
    uid = StringField(primary_key=True, default=node_id("Runner"))
    name = StringField(required=True)
    variant = StringField(required=True)
    stats = ListField(IntField(), required=True, validation=fixed_length(5))
    created_at = DateTimeField(default=lambda: datetime.utcnow())
    # skills = EmbeddedDocumentField


connect('mongotest',
        host="localhost",
        username="root",
        password="root",
        authentication_source='admin')

for runner in [Runner(name="ゴールドシップ", variant="レッドストライフ", stats=[1000, 1200, 1000, 350, 450]),
               Runner(name="メジロマックイーン", variant="エレガンス・ライン", stats=[1000, 1200, 1000, 350, 450])]:
    print("----------")
    print(runner.id)
    print(runner.uid)
    runner.save()
    print(runner.id)
