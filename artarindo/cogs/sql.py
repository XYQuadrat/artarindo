import datetime
from traceback import print_tb
from peewee import fn, Select

from .user_info import UserInfo
from ..meme_model import MediaItem, db


def insert_meme(
    filename: str, score, author: str, url: str, created_at: datetime.datetime
) -> None:
    item = MediaItem(
        filename=filename,
        score=score,
        author=author,
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


# BELOW: STAT FUNCTIONS


def user_has_records(user: str) -> bool:
    return MediaItem.select().where(MediaItem.author == user).exists()


def user_get_score_info(user: str, info: UserInfo) -> None:
    scoreboard = MediaItem.select(
        MediaItem.author,
        fn.AVG(MediaItem.score).alias("score_avg"),
        fn.RANK().over(order_by=[fn.AVG(MediaItem.score).desc()]).alias("score_rank"),
    ).group_by(MediaItem.author)

    user_score_info = (
        Select(columns=[scoreboard.c.score_avg, scoreboard.c.score_rank])
        .from_(scoreboard)
        .where(scoreboard.c.author == user)
        .bind(db)
        .get()
    )

    info.score_avg = user_score_info["score_avg"]
    info.score_rank = user_score_info["score_rank"]


def user_get_count_info(user: str, info: UserInfo) -> None:
    scoreboard = MediaItem.select(
        MediaItem.author,
        fn.COUNT(MediaItem.id).alias("count"),
        fn.RANK().over(order_by=[fn.COUNT(MediaItem.id).desc()]).alias("count_rank"),
    ).group_by(MediaItem.author)

    user_count_info = (
        Select(columns=[scoreboard.c.count, scoreboard.c.count_rank])
        .from_(scoreboard)
        .where(scoreboard.c.author == user)
        .bind(db)
        .get()
    )

    info.count = user_count_info["count"]
    info.count_rank = user_count_info["count_rank"]


def user_get_hindex(user: str, info: UserInfo) -> None:
    hindexes = MediaItem.select(
        MediaItem.author,
        MediaItem.score,
        fn.ROW_NUMBER()
        .over(partition_by=[MediaItem.author], order_by=[MediaItem.score.desc()])
        .alias("ranking"),
    ).alias("subq")

    query = (
        hindexes.select(fn.MAX(hindexes.c.ranking))
        .from_(hindexes)
        .where(hindexes.c.ranking <= hindexes.c.score and hindexes.c.author == user)
        .group_by(hindexes.c.author)
        .order_by(fn.MAX(hindexes.c.ranking).desc())
    )

    info.hindex = query.get().ranking
