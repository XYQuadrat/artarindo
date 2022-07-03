import sqlite3

from cogs.memeinfo import UserInfo


def connect() -> sqlite3.Connection:
    con = sqlite3.connect("data/memes.db")
    return con


def insert_meme(con: sqlite3.Connection, name: str, score, author: str):
    con.execute(
        """INSERT INTO MediaItem(Filename, Score, Author)
           VALUES(?,?,?)""",
        (name, score, author),
    )
    con.commit()


def exists_record(con: sqlite3.Connection, filename: str) -> bool:
    row = con.execute(
        """SELECT EXISTS(
        SELECT 1
        FROM MediaItem
        WHERE Filename = :name)""",
        {"name": filename},
    ).fetchone()[0]

    return row


def update_score(con: sqlite3.Connection, filename: str, score: int):
    con.execute(
        """UPDATE MediaItem
        SET Score = :new_score
        WHERE Filename = :filename""",
        {"new_score": score, "filename": filename},
    )
    con.commit()


# BELOW: STAT FUNCTIONS


def user_has_records(con: sqlite3.Connection, user: str) -> bool:
    return con.execute(
        """SELECT EXISTS
        (SELECT 1
        FROM MediaItem
        WHERE Author = :user)""",
        {"user": user},
    ).fetchone()[0]


def user_get_score_info(con: sqlite3.Connection, user: str, info: UserInfo):
    row = con.execute(
        """SELECT ScoreAvg, ScoreRank
        FROM (SELECT Author, AVG(Score) as ScoreAvg, RANK() OVER (ORDER BY AVG(Score) DESC) ScoreRank
        FROM MediaItem
        GROUP BY Author)
        WHERE Author = :user""",
        {"user": user},
    ).fetchone()

    info.score_avg = row[0]
    info.score_rank = row[1]


def user_get_count_info(con: sqlite3.Connection, user: str, info: UserInfo):
    row = con.execute(
        """SELECT Count, CountRank
        FROM (SELECT Author, COUNT(Id) as Count, RANK() OVER (ORDER BY Count(Id) DESC) CountRank
        FROM MediaItem
        GROUP BY Author)
        WHERE Author = :user""",
        {"user": user},
    ).fetchone()

    info.count = row[0]
    info.count_rank = row[1]


def user_get_hindex(con: sqlite3.Connection, user: str, info: UserInfo):
    row = con.execute(
        """SELECT MAX(Ranking)
        FROM (SELECT Author, Score, ROW_NUMBER() OVER (PARTITION BY Author ORDER BY Score DESC) AS Ranking
            FROM MediaItem)
        WHERE Ranking <= Score AND Author = :user
        GROUP BY Author
        ORDER BY MAX(Ranking) DESC""",
        {"user": user},
    ).fetchone()

    info.hindex = row[0]
