from datetime import datetime
from peewee import *

db = SqliteDatabase("../data/button.db")


class BaseModel(Model):
    class Meta:
        database = db


class Challenge(BaseModel):
    name = CharField()
    created_date = DateTimeField(default=datetime.now)
    solved_date = DateTimeField(NULL=True)
    solver = CharField(NULL=True)
