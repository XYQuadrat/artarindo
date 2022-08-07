import sqlite3

from cogs.memeinfo import UserInfo


def connect() -> sqlite3.Connection:
    con = sqlite3.connect("data/memes.db")
    return con


def insert_meme(con: sqlite3.Connection, name: str, score, author: str):
    con.execute(
        """INSERT INTO media_item(filename, score, author)
           VALUES(?,?,?)""",
        (name, score, author),
    )
    con.commit()


def exists_record(con: sqlite3.Connection, filename: str) -> bool:
    row = con.execute(
        """SELECT EXISTS(
        SELECT 1
        FROM media_item
        WHERE filename = :name)""",
        {"name": filename},
    ).fetchone()[0]

    return row


def update_score(con: sqlite3.Connection, filename: str, score: int):
    con.execute(
        """UPDATE media_item
        SET score = :new_score
        WHERE filename = :filename""",
        {"new_score": score, "filename": filename},
    )
    con.commit()


# BELOW: STAT FUNCTIONS


def user_has_records(con: sqlite3.Connection, user: str) -> bool:
    return con.execute(
        """SELECT EXISTS
        (SELECT 1
        FROM media_item
        WHERE author = :user)""",
        {"user": user},
    ).fetchone()[0]


def user_get_score_info(con: sqlite3.Connection, user: str, info: UserInfo):
    row = con.execute(
        """SELECT ScoreAvg, ScoreRank
        FROM (SELECT author, AVG(score) as ScoreAvg, RANK() OVER (ORDER BY AVG(score) DESC) ScoreRank
        FROM media_item
        GROUP BY author)
        WHERE author = :user""",
        {"user": user},
    ).fetchone()

    info.score_avg = row[0]
    info.score_rank = row[1]


def user_get_count_info(con: sqlite3.Connection, user: str, info: UserInfo):
    row = con.execute(
        """SELECT Count, CountRank
        FROM (SELECT author, COUNT(id) as Count, RANK() OVER (ORDER BY Count(id) DESC) CountRank
        FROM media_item
        GROUP BY author)
        WHERE author = :user""",
        {"user": user},
    ).fetchone()

    info.count = row[0]
    info.count_rank = row[1]


def user_get_hindex(con: sqlite3.Connection, user: str, info: UserInfo):
    row = con.execute(
        """SELECT MAX(Ranking)
        FROM (SELECT author, score, ROW_NUMBER() OVER (PARTITION BY author ORDER BY score DESC) AS Ranking
            FROM media_item)
        WHERE Ranking <= score AND author = :user
        GROUP BY author
        ORDER BY MAX(Ranking) DESC""",
        {"user": user},
    ).fetchone()

    info.hindex = row[0]
