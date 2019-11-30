#Original YiffScraper by shubham418
#Update Project Manager: LaChocola
#Update Coder: DigiDuncan

import sys
import os
import requests
import re
import html
import errno
from bs4 import BeautifulSoup

checkstrings = ["patreon_data", "patreon_inline", "shared_data"]
with open("./currentcookie.txt") as f:
    currentcookie = f.readlines()
currentcookie = [x.strip() for x in currentcookie]
currentcookie = currentcookie[0]

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
    lst = URL.rsplit('/')
    name = lst[-1]
    name = name.replace('%20', '_')
    return name

# Returns lst containing all files
def getLinks(URL):
    response = requests.get(URL)
    soup = BeautifulSoup(response.content, "html.parser")

    links = soup.find_all('a')
    unfin_paths = []
    for link in links:
        href = link.get('href')
        if href is None:
            continue
        # Check if link is of data
        for string in checkstrings:
            if string in href:
                if re.match("\/.+\/\d+\/\d+\/\d+\/.+$", href):
                    unfin_paths.append(href)
    fin_paths = []
    for path in unfin_paths:
        fin_paths.append(URL + path)
    return fin_paths

def download(URL, name):
    pathtosaveto = f"Scrapes/{name}/"
    filename = getFileName(URL)
    fullpath = pathtosaveto + filename

    #TODO: Don't overwrite files.

    mkdir(pathtosaveto)

    in_file = requests.get(URL, stream=True)
    out_file = open(fullpath, 'wb')
    for chunk in in_file.iter_content(chunk_size=8192):
        out_file.write(chunk)
    out_file.close()

#Get the URL of the page we're scraping.
def getYiffPage(URL):

    response = requests.get(URL)
    soup = BeautifulSoup(response.content, "html.parser")

    if "patreon.com" in URL:
        idsearch = re.search("https:\/\/www\.patreon\.com\/api\/user\/(\d+)", str(soup))
        if idsearch: idtag = idsearch.group(1)
        URL = f"http://yiff.party/patreon/{idtag}"
    elif re.match("\d+$", URL):
        idtag = URL
        URL = f"http://yiff.party/patreon/{idtag}"
    elif "yiff.party" in URL:
        pass
    else:
        URL = None
        print("Please input either a Patreon or a yiff.party link.")
    return URL

#Get the name of the creator.
def getYiffName(URL):

    name = None

    response = requests.get(URL)
    soup = BeautifulSoup(response.content, "html.parser")

    name_element = re.search('<meta content="(.*) is creating', str(soup))
    if name_element: name = name_element.group(1)

    return name

#Scrape each project.
def scrape(project):
    patreonname = getYiffName(project)
    yiffpage = getYiffPage(project)

    #TODO: Detect 404's from y.p.

    print(f"Scraping {patreonname}: {yiffpage}")

    links = getLinks(yiffpage)
    for link in links:
        #TODO: Progress bar.
        download(link, patreonname)

#Main program.
if __name__ == "__main__":
    projects = sys.argv[1:]
    print("""
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
