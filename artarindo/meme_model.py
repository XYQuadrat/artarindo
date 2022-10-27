from peewee import (
    SqliteDatabase,
    Model,
    TextField,
    DateTimeField,
    CompositeKey,
    IntegerField,
    ForeignKeyField,
)
from . import config

db = SqliteDatabase(config.DATA_PATH + "memes.db")


class BaseModel(Model):
    class Meta:
        database = db
        legacy_table_names = False


class MediaItem(BaseModel):
    filename = TextField(null=False)
    score = IntegerField()
    author_id = TextField(default="00000")
    message_url = TextField(null=True)
    created_date = DateTimeField(null=True)


class Tag(BaseModel):
    name = TextField()


class MediaItemTag(BaseModel):
    media_item_id = ForeignKeyField(MediaItem, backref="tags")
    tag_id = ForeignKeyField(Tag, backref="media_items")

    class Meta:
        primary_key = CompositeKey("media_item_id", "tag_id")


def connect():
    db.connect(reuse_if_open=True)


def disconnect():
    db.close()
