import os
import functools
from datetime import datetime
import time
from pathlib import Path

from dateutil.parser import parse as parsedate
from dateutil import tz
import aiohttp


def retryrequest(status_code=None, retries=4):
    if status_code is None:
        status_code = range(500, 600)
    if not isinstance(status_code, (list, tuple)):
        status_code = [status_code]

    def decorator_retry(func):
        @functools.wraps(func)
        async def wrapper_retry(*args, **kwargs):
            tries = 0
            while True:
                tries += 1
                try:
                    result = await func(*args, **kwargs)
                    break
                except aiohttp.ClientResponseError as e:
                    if e.status not in status_code:
                        raise
                    if tries >= retries:
                        raise
            return result
        return wrapper_retry
    return decorator_retry


def getFileTime(path):
    try:
        file_datetime = datetime.fromtimestamp(os.path.getmtime(path), tz=tz.tzutc())
    except FileNotFoundError:
        file_datetime = None
    return file_datetime


def getUrlTime(response):
    if "last-modified" not in response.headers:
        return None
    return parsedate(response.headers["last-modified"])


def getUrlTimestamp(response):
    url_time = getUrlTime(response)
    if url_time is None:
        return None
    url_timestamp = time.mktime(url_time.timetuple())
    return url_timestamp


async def needsUpdate(session, url, path):
    response = await session.head(url, allow_redirects=True)
    url_time = getUrlTime(response)
    file_time = getFileTime(path)
    if url_time is None or file_time is None:
        return True
    return url_time > file_time


async def download(session, url, path, update):
    path = Path(path)
    if update and not await needsUpdate(session, url, path):
        return
    path.parent.mkdir(exist_ok=True)
    response = await session.get(url)
    with open(path, "wb") as out_file:
        while True:
            chunk = await response.content.read(8192)
            if not chunk:
                break
            out_file.write(chunk)
        url_timestamp = getUrlTimestamp(response)
        os.utime(path, (url_timestamp, url_timestamp))
