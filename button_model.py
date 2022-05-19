from datetime import datetime
from email.policy import default
from peewee import *

db = SqliteDatabase("data/button.db")


class BaseModel(Model):
    class Meta:
        database = db


class Challenge(BaseModel):
    name = CharField()
    created_date = DateTimeField(default=datetime.now)
    solved_date = DateTimeField(null=True)
    solver = CharField(null=True)
    points = IntegerField(default=0)


db.create_tables([Challenge])
