import sqlite3
import typing


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
        """SELECT EXISTS(SELECT 1 FROM MediaItem WHERE Filename = :name)""",
        {"name": filename},
    ).fetchone()[0]

    return row


def update_score(con: sqlite3.Connection, filename: str, score: int):
    con.execute(
        """UPDATE MediaItem SET Score = :new_score WHERE Filename = :filename""",
        {"new_score": score, "filename": filename},
    )
    con.commit()
