# Original YiffScraper by shubham418
# Update Project Manager: LaChocola
# Update Coder: DigiDuncan
# Bug fixer: Natalie Fearnley

import re
import sys
import os
import errno

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


# download a file
def download(URL, name):
    pathtosaveto = f"scrapes/{name}/"
    filename = getFileName(URL)
    fullpath = pathtosaveto + filename

    # TODO: Don't overwrite files.

    mkdir(pathtosaveto)

    in_file = requests.get(URL, stream=True)
    with open(fullpath, "wb") as out_file:
        for chunk in in_file.iter_content(chunk_size=8192):
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
def getFileName(URL):
    lst = URL.rsplit("/")
    name = lst[-1]
    name = name.replace("%20", "_")
    return name


# Returns list containing all file urls
def getLinks(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")

    links = [elem.get("href") for elem in tqdm(soup.find_all("a")) if elem.get("href") is not None]

    datalinks = [link for link in links if isDataLink(link)]

    abspaths = [url + path for path in datalinks]

    return abspaths


# Check if the given url is a data link
def isDataLink(url):
    checkstrings = ["patreon_data", "patreon_inline", "shared_data"]
    # Check if link is of data
    for s in checkstrings:
        if s in url and re.match(r"/.+/\d+/\d+/\d+/.+$", url):
            return True
    return False

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
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")

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


# Scrape a project
def scrape(arg):
    info = getProjectInfo(arg)
    if info is None:
        print(f"Invalid argument: {arg}")
        print("Please enter a patreon id, Patreon url, or yiff.party url")
        return

    print(f"Scraping {info.name}: {info.yiffurl}")

    # TODO: Detect 404s from yiff.party
    print(f"Getting links: {info.yiffurl}")
    links = getLinks(info.yiffurl)

    print(f"Downloading links: {len(links)}")
    for link in tqdm(links):
        print(link)
        # TODO: Progress bar
        download(link, info.name)


# Scrape all the projects
def main():
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
        scrape(project)

    print("\n*******************************************************************************\n")
    print("\nAll projects done!\n")
    print("\nEnjoy ;)")


# Main program.
if __name__ == "__main__":
    main()
