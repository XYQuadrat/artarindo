import datetime
from peewee import fn, Select

from .user_info import UserInfo
from ..meme_model import MediaItem, Username, db


def insert_meme(
    filename: str, score, author_id: int, url: str, created_at: datetime.datetime
) -> None:
    item = MediaItem(
        filename=filename,
        score=score,
        author_id=author_id,
        message_url=url,
        created_date=created_at,
    )
    item.save()


def exists_record(filename: str) -> bool:
    return MediaItem.select().where(MediaItem.filename == filename).exists()


def update_score(filename: str, score: int) -> None:
    item = MediaItem.get(MediaItem.filename == filename)
    item.score = score
    item.save()


def save_username_mapping(username: str, id: int) -> None:
    item, created = Username.get_or_create(author_id=id)
    if not created:
        item.username = username
    item.save()


# BELOW: STAT FUNCTIONS


def user_has_records(user_id: int) -> bool:
    return MediaItem.select().where(MediaItem.author_id == user_id).exists()


def user_get_score_info(user_id: int, info: UserInfo) -> None:
    scoreboard = MediaItem.select(
        MediaItem.author_id,
        fn.AVG(MediaItem.score).alias("score_avg"),
        fn.RANK().over(order_by=[fn.AVG(MediaItem.score).desc()]).alias("score_rank"),
    ).group_by(MediaItem.author_id)

    user_score_info = (
        Select(columns=[scoreboard.c.score_avg, scoreboard.c.score_rank])
        .from_(scoreboard)
        .where(scoreboard.c.author_id == user_id)
        .bind(db)
        .get()
    )

    info.score_avg = user_score_info["score_avg"]
    info.score_rank = user_score_info["score_rank"]


def user_get_count_info(user_id: int, info: UserInfo) -> None:
    scoreboard = MediaItem.select(
        MediaItem.author_id,
        fn.COUNT(MediaItem.id).alias("count"),
        fn.RANK().over(order_by=[fn.COUNT(MediaItem.id).desc()]).alias("count_rank"),
    ).group_by(MediaItem.author_id)

    user_count_info = (
        Select(columns=[scoreboard.c.count, scoreboard.c.count_rank])
        .from_(scoreboard)
        .where(scoreboard.c.author_id == user_id)
        .bind(db)
        .get()
    )

    info.count = user_count_info["count"]
    info.count_rank = user_count_info["count_rank"]


def user_get_hindex(user_id: id, info: UserInfo) -> None:
    hindexes = MediaItem.select(
        MediaItem.author_id,
        MediaItem.score,
        fn.ROW_NUMBER()
        .over(partition_by=[MediaItem.author_id], order_by=[MediaItem.score.desc()])
        .alias("ranking"),
    ).alias("subq")

    query = (
        hindexes.select(fn.MAX(hindexes.c.ranking))
        .from_(hindexes)
        .where(hindexes.c.ranking <= hindexes.c.score, hindexes.c.author_id == user_id)
        .group_by(hindexes.c.author_id)
        .order_by(fn.MAX(hindexes.c.ranking).desc())
    )

    info.hindex = query.get().ranking
