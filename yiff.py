# Original YiffScraper by shubham418
# Update Project Manager: LaChocola
# Update Coder: DigiDuncan
# Bug fixer: Natalie Fearnley

import re
import sys
import os
import errno
import urllib

import requests
from bs4 import BeautifulSoup
from tqdm import tqdm


class ProjectInfo:
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

    def __str__(self):
        return f"{self.name} ({self.id})"

    def __repr__(self):
        return f"ProjectInfo(id={self.id!r}, name={self.name!r}, patreonurl={self.patreonurl!r})"


# download a file
def download(url, name):
    pathtosaveto = f"scrapes/{name}/"
    filename = getFileName(url)
    fullpath = pathtosaveto + filename

    # TODO: Don't overwrite files

    mkdir(pathtosaveto)

    r = requests.get(url, stream=True)
    r.raise_for_status()
    with open(fullpath, "wb") as out_file:
        for chunk in r.iter_content(chunk_size=8192):
            out_file.write(chunk)


def mkdir(path):
    try:
        os.makedirs(path)
    except OSError as exc:  # Python >2.5
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise


# Returns the name of the file
def getFileName(url):
    lst = url.rsplit("/")
    name = lst[-1]
    name = name.replace("%20", "_")
    return name


# Returns list containing all file urls
def getLinks(url):
    s = initSession()
    r = s.get(url)
    r.raise_for_status()
    soup = BeautifulSoup(r.content, "html.parser")

    links = [elem.get("href") for elem in soup.find_all("a") if elem.get("href") is not None]

    datalinks = [link for link in links if isDataLink(link)]

    abspaths = [urllib.parse.urljoin(url, path) for path in datalinks]

    return abspaths


# Check if the given url is a data link
def isDataLink(url):
    return re.match(r"/(patreon_data|patreon_inline|shared_data)/\d+/\d+/.+$", url) is not None


# get creator name, patreod id, patreon url and yiff url
def getProjectInfoFromYiffUrl(url):
    match = re.search(r"yiff.party/(?:patreon/)?(\d+)", url)
    if match is None:
        return None
    patreonid = match.group(1)
    return getProjectInfoFromPatreonId(patreonid)


# get creator name, patreod id, patreon url and yiff url
def getProjectInfoFromPatreonId(patreonid):
    url = f"https://www.patreon.com/user?u={patreonid}"
    return getProjectInfoFromPatreonUrl(url)


# get creator name, patreod id, patreon url and yiff url
def getProjectInfoFromPatreonUrl(url):
    r = requests.get(url)
    r.raise_for_status()
    soup = BeautifulSoup(r.content, "html.parser")

    info = ProjectInfo()
    info.name = scrapeNameFromPatreon(soup)
    info.id = scrapeIdFromPatreon(soup)
    info.patreonurl = scrapeUrlFromPatreon(soup)

    return info


# scrape creator name from patreon page
def scrapeNameFromPatreon(soup):
    elem = soup.find("meta", attrs={"name": "title"})
    if elem is None:
        return None

    title = elem["content"]
    match = re.search("(.*) (?:are|is) creating", title)
    if match is None:
        return None

    name = match.group(1)

    return name


# scrape id from patreon page
def scrapeIdFromPatreon(soup):
    patreonid = None
    match = re.search(r"https://www.patreon.com/api/user/(\d+)", str(soup))
    if match is not None:
        patreonid = match.group(1)
    return patreonid


# scrape url from patreon page
def scrapeUrlFromPatreon(soup):
    elem = soup.find("meta", attrs={"name": "canonicalURL"})
    if elem is None:
        return None

    url = elem["content"]

    return url


# Takes a patreon id, patreon url, or yiff url
# Returns project name, patreon id, patreon url, and yiff url
def getProjectInfo(arg):
    info = None

    if re.match(r"\d+$", arg):
        # patreon id
        info = getProjectInfoFromPatreonId(arg)
    elif "patreon.com" in arg:
        # patreon url
        info = getProjectInfoFromPatreonUrl(arg)
    elif "yiff.party/patreon/" in arg or "yiff.party/" in arg:
        # yiff url
        info = getProjectInfoFromYiffUrl(arg)

    return info


def initSession():
    s = requests.session()
    r = s.post("https://yiff.party/config", data={"a": "post_view_limit", "d": "all"})
    r.raise_for_status()
    return s


# Scrape a project
def scrape(arg):
    try:
        info = getProjectInfo(arg)
        if info is None:
            print(f"Invalid argument: {arg}")
            print("Please enter a patreon id, Patreon url, or yiff.party url")
            return

        print(f"Scraping {info.name} ({info.yiffurl})")

        # TODO: Detect 404s from yiff.party
        print("Getting links")
        links = getLinks(info.yiffurl)

        print(f"Downloading {len(links)} links")
        t = tqdm(links, unit="file")
        for link in t:
            t.set_description(getFileName(link))
            download(link, info.name)
    except requests.exceptions.HTTPError as e:
        print(e)


# Scrape all the projects
def main():
    projects = sys.argv[1:]
    projects = ["http://yiff.party/patreon/7330723"]
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
        scrape(project)

    print("\n*******************************************************************************\n")
    print("\nAll projects done!\n")
    print("\nEnjoy ;)")


# Main program.
if __name__ == "__main__":
    main()
