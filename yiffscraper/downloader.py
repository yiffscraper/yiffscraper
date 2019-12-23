import os
from datetime import datetime
import time
from pathlib import Path
import asyncio

from dateutil.parser import parse as parsedate
from dateutil import tz
import aiohttp


class UrlItem:
    __slots__ = ("url", "size", "lastModified", "path")

    def __init__(self, url, size, lastModified, path=None):
        self.url = url
        self.size = size
        self.lastModified = lastModified
        self.path = path

    def needsUpdate(self):
        if self.path is None:
            return False
        fileLastModified = getFileTime(self.path)
        if self.lastModified is None or fileLastModified is None:
            return True
        return self.lastModified > fileLastModified

    @classmethod
    async def fetchMetadata(cls, session, url, path=None):
        async with session.head(url, allow_redirects=True) as response:
            try:
                response.raise_for_status()
            except aiohttp.ClientResponseError as e:
                # I don't like returning Exceptions, but I can't find a better way to pass a single error in an async loop
                return (None, e)
            size = int(response.headers.get("content-length", 0))
            lastModified = parsedateOrNone(response.headers.get("last-modified", None))
        return (cls(url, size, lastModified, path), None)

    async def download(self, session, update):
        if self.path is None:
            return
        if update and not await self.needsUpdate():
            return

        Path(self.path).parent.mkdir(parents=True, exist_ok=True)

        async with session.get(self.url) as response:
            try:
                response.raise_for_status()
            except aiohttp.ClientResponseError as e:
                # I don't like returning Exceptions, but I can't find a better way to pass a single error in an async loop
                return (self, e)
            with open(self.path, "wb") as out_file:
                while True:
                    chunk = await response.content.read(8192)
                    if not chunk:
                        break
                    out_file.write(chunk)

        url_timestamp = getTimestamp(self.lastModified)
        os.utime(self.path, (url_timestamp, url_timestamp))
        return (self, None)

    @classmethod
    async def fetchAllMetadata(cls, items):
        connector = aiohttp.connector.TCPConnector(limit=25, limit_per_host=10)
        timeout = aiohttp.ClientTimeout(total=60)
        async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
            tasks = [cls.fetch(session, i.url, i.path) for i in items]
            for task in asyncio.as_completed(tasks):
                urlitem = await task
                yield urlitem

    @classmethod
    async def downloadAll(cls, urlitems, update):
        connector = aiohttp.connector.TCPConnector(limit=25, limit_per_host=10)
        timeout = aiohttp.ClientTimeout(total=60)
        async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
            tasks = [urlitem.download(session, update) for urlitem in urlitems]
            for task in asyncio.as_completed(tasks):
                yield await task

    def __len__(self):
        return self.size


def getFileTime(path):
    try:
        file_datetime = datetime.fromtimestamp(os.path.getmtime(path), tz=tz.tzutc())
    except FileNotFoundError:
        file_datetime = None
    return file_datetime


def getTimestamp(t):
    if t is None:
        return None
    timestamp = time.mktime(t.timetuple())
    return timestamp


def parsedateOrNone(dateString):
    if dateString is None:
        return None
    return parsedate(dateString)
