import pytest
from artarindo.cogs import sql


def test_exists_record():
    assert sql.exists_record("966405010046988338.jpg") is True
    assert sql.exists_record("abcdefghi.jpg") is False


def test_user_has_records():
    assert sql.user_has_records("XYQuadrat#6502") is True
    assert sql.user_has_records("abc#99999") is False
