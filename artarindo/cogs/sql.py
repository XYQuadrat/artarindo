import datetime
import logging
from peewee import fn

from .user_info import UserInfo
from ..meme_model import MediaItem


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


def update_data(filename: str, url: str, created_at: datetime.datetime) -> None:
    if not url or not created_at:
        logging.warn("Did not get URL or creation date for item " + filename)

    item = MediaItem.get(MediaItem.filename == filename)
    item.message_url = url
    item.created_date = created_at
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
        scoreboard.select(MediaItem.score_avg, MediaItem.score_rank)
        .where(MediaItem.author == user)
        .get()
    )

    info.score_avg = user_score_info.score_avg
    info.score_rank = user_score_info.score_rank


def user_get_count_info(user: str, info: UserInfo) -> None:
    scoreboard = MediaItem.select(
        MediaItem.author,
        fn.COUNT(MediaItem.index).alias("count"),
        fn.RANK().over(order_by=[fn.COUNT(MediaItem.index).desc()]).alias("count_rank"),
    ).group_by(MediaItem.author)

    user_count_info = (
        scoreboard.select(MediaItem.count, MediaItem.count_rank)
        .where(MediaItem.author == user)
        .get()
    )

    info.count = user_count_info.count
    info.count_rank = user_count_info.count_rank


def user_get_hindex(user: str, info: UserInfo) -> None:
    hindexes = MediaItem.select(
        MediaItem.author,
        MediaItem.score,
        fn.ROW_NUMBER()
        .over(partition_by=[MediaItem.author], order_by=[MediaItem.score.desc()])
        .alias("ranking"),
    )

    info.hindex = (
        hindexes.select(fn.MAX(hindexes.ranking))
        .where(hindexes.ranking <= hindexes.score and hindexes.author == user)
        .group_by(hindexes.author)
        .order_by(fn.MAX(hindexes.ranking).desc())
        .get()
    )
