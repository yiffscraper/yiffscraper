# Original YiffScraper by shubham418
# Update Project Manager: LaChocola
# Update Coder: DigiDuncan
# Bug fixer: Natalie Fearnley

import asyncio
import re
import sys
import urllib.parse
from pathlib import Path, PurePosixPath

import aiohttp
import requests
from bs4 import BeautifulSoup
from tqdm import tqdm

from httperrors import retryrequest


class PatreonScraper:
    def __init__(self, soup):
        self.soup = soup

    @property
    def name(self):
        elem = self.soup.find("meta", attrs={"name": "title"})
        if elem is None:
            return None

        title = elem["content"]
        match = re.search("(.*) (?:are|is) creating", title)
        if match is None:
            return None

        name = match.group(1)

        return name

    @property
    def id(self):
        patreonid = None
        match = re.search(r"https://www.patreon.com/api/user/(\d+)", str(self.soup))
        if match is not None:
            patreonid = match.group(1)
        return patreonid

    @property
    def url(self):
        elem = self.soup.find("meta", attrs={"name": "canonicalURL"})
        if elem is None:
            return None

        url = elem["content"]

        return url


class Project:
    def __init__(self):
        self.id = ""
        self.name = ""
        self.patreonurl = ""

    @property
    def yiffurl(self):
        url = f"http://yiff.party/patreon/{self.id}"
        return url

    @property
    def yiffapiurl(self):
        url = f"http://yiff.party/{self.id}.json"
        return url

    @property
    def path(self):
        path = Path("scrapes") / self.name
        return path

    # Returns list containing all project times
    def getItems(self):
        s = self.initSession()
        r = s.get(self.yiffurl)
        r.raise_for_status()
        soup = BeautifulSoup(r.content, "html.parser")

        links = [elem.get("href") for elem in soup.find_all("a") if elem.get("href") is not None]

        datalinks = [link for link in links if self.isDataLink(link)]

        abspaths = [urllib.parse.urljoin(self.yiffurl, path) for path in datalinks]

        items = [ProjectItem(self, url) for url in abspaths]

        return items

    @classmethod
    def initSession(cls):
        s = requests.session()
        r = s.post("https://yiff.party/config", data={"a": "post_view_limit", "d": "all"})
        r.raise_for_status()
        return s

    # Check if the given url is a data link
    @classmethod
    def isDataLink(cls, url):
        return re.match(r"/(patreon_data|patreon_inline|shared_data)/\d+/\d+/.+$", url) is not None

    # Takes a patreon id, patreon url, or yiff url
    # Returns a Project object
    @classmethod
    def get(cls, arg):
        patreonurl = None
        if "patreon.com" in arg:
            patreonurl = arg
        elif re.match(r"\d+$", arg):
            patreonid = arg
            patreonurl = f"https://www.patreon.com/user?u={patreonid}"
        elif "yiff.party/patreon/" in arg or "yiff.party/" in arg:
            yiffurl = arg
            match = re.search(r"yiff.party/(?:patreon/)?(\d+)", yiffurl)
            if match is None:
                return None
            patreonid = match.group(1)
            patreonurl = f"https://www.patreon.com/user?u={patreonid}"

        if patreonurl is None:
            return None

        return cls.getFromPatreonUrl(patreonurl)

    @classmethod
    def getFromPatreonUrl(cls, patreonurl):
        r = requests.get(patreonurl)
        r.raise_for_status()
        soup = BeautifulSoup(r.content, "html.parser")
        scraper = PatreonScraper(soup)

        project = Project()
        project.name = scraper.name
        project.id = scraper.id
        project.patreonurl = scraper.url

        return project

    def __str__(self):
        return f"{self.name} ({self.id})"

    def __repr__(self):
        return f"{type(self).__name__}(id={self.id!r}, name={self.name!r}, patreonurl={self.patreonurl!r})"


class ProjectItem:
    def __init__(self, project, url):
        self.project = project
        self.url = url
        self.filename = self.getFilename(url)

    @property
    def fullpath(self):
        return self.project.path / self.filename

    @retryrequest(504, outfunc=tqdm.write)
    async def download(self, session):
        self.fullpath.parent.mkdir(exist_ok=True)
        r = await session.get(self.url)
        with open(self.fullpath, "wb") as out_file:
            while True:
                chunk = await r.content.read(8192)
                if not chunk:
                    break
                out_file.write(chunk)

    def __str__(self):
        return self.url

    # Replace quoted and unquoted unsafe characters in a path
    @classmethod
    def makeUrlPathSafe(cls, pathstr):
        unsafe = list('\\:*?"<>| ')
        unsafe += [urllib.parse.quote(c, safe="").upper() for c in '\\/:*?"<>| ']
        unsafe += [urllib.parse.quote(c, safe="").lower() for c in '\\/:*?"<>| ']
        for c in unsafe:
            pathstr = pathstr.replace(c, "_")
        return pathstr

    # Returns the name of the file
    @classmethod
    def getFilename(cls, url):
        pathstr = urllib.parse.urlparse(url).path
        safepathstr = cls.makeUrlPathSafe(pathstr)
        unquotedpathstr = urllib.parse.unquote(safepathstr)
        path = "_".join(PurePosixPath(unquotedpathstr).parts[-2:])
        return path


async def downloadAll(items):
    connector = aiohttp.connector.TCPConnector(limit=25, limit_per_host=10)
    async with aiohttp.ClientSession(connector=connector, raise_for_status=True) as session:
        tasks = [item.download(session) for item in items]
        for task in tqdm(asyncio.as_completed(tasks), total=len(tasks), unit="file"):
            try:
                await task
            except aiohttp.ClientResponseError as e:
                tqdm.write(f"{e.status} failed to download {e.request_info.url}")


async def scrape(arg):
    project = Project.get(arg)
    if project is None:
        print(f"Invalid argument: {arg}")
        print("Please enter a patreon id, Patreon url, or yiff.party url")
        return

    print(f"Scraping {project})")

    print("Getting links")
    items = project.getItems()

    print(f"Downloading {len(items)} links")
    await downloadAll(items)


# Scrape all the projects
async def main():
    projects = sys.argv[1:]
    print(r"""
 __     ___  __  __ _____
 \ \   / (_)/ _|/ _/ ____|
  \ \_/ / _| |_| || (___   ___ _ __ __ _ _ __   ___ _ __
   \   / | |  _|  _\___ \ / __| '__/ _` | '_ \ / _ \ '__|
    | |  | | | | | ____) | (__| | | (_| | |_) |  __/ |
    |_|  |_|_| |_||_____/ \___|_|  \__,_| .__/ \___|_|
                                        | |
                                        |_|
    """)

    for project in projects:
        try:
            await scrape(project)
        except requests.exceptions.HTTPError as e:
            print(e)

    print("\nAll projects done!\n")
    print("\nEnjoy ;)")


# Main program.
if __name__ == "__main__":
    asyncio.run(main())
