from datetime import datetime
from peewee import SqliteDatabase, Model, CharField, DateTimeField, IntegerField
from . import config

db = SqliteDatabase(config.DATA_PATH + "button.db")


class BaseModel(Model):
    class Meta:
        database = db


class Challenge(BaseModel):
    name = CharField()
    created_date = DateTimeField(default=datetime.now)
    solved_date = DateTimeField(null=True)
    solver = CharField(null=True)
    points = IntegerField(default=0)


def connect():
    db.connect(reuse_if_open=True)


def disconnect():
    db.close()
