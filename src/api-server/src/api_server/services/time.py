"""General purpose utilities."""

import datetime


def utc_datetime() -> datetime.datetime:
    return datetime.datetime.now(datetime.UTC)
