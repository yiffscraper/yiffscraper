import sys
import asyncio
from pathlib import Path

from aiohttp import ClientResponseError

from requests.exceptions import HTTPError
from tqdm import tqdm

from yiffscraper.yiffscraper import Project, YiffException
from yiffscraper.downloader import UrlItem


class YiffArgs:
    __slots__ = ("commandName", "projects", "update", "help")

    def __init__(self, commandName, projectArgs, updateFlag, helpFlag):
        self.commandName = commandName
        self.projects = projectArgs
        self.update = updateFlag
        self.help = helpFlag

    @classmethod
    def parse(cls):
        args = sys.argv[1:]
        commandName = Path(sys.argv[0]).name
        projectArgs = [a for a in args if not a.startswith("--")]
        updateFlag = "--update" in args
        helpFlag = "--help" in args
        return cls(commandName, projectArgs, updateFlag, helpFlag)


# Scrape all the projects
async def scrape():
    try:
        print(r"   __     ___  ___ __ _____""\n"
              r"   \ \   / (_)/ _// _/ ____|""\n"
              r"    \ \_/ / _| |_| || (___   ___ _ __ __ _ _ __   ___ _ __""\n"
              r"     \   / | |  _|  _\___ \ / __| '__/ _` | '_ \ / _ \ '__|""\n"
              r"      | |  | | | | | ____) | (__| | | (_| | |_) |  __/ |""\n"
              r"      |_|  |_|_| |_||_____/ \___|_|  \__,_| .__/ \___|_|""\n"
              r"                                          | |""\n"
              r"                                          |_|""\n")

        args = YiffArgs.parse()
        if args.help or not args.projects:
            print(f"{args.commandName} [--help] [--update] [patreonid/patreonurl/yiffpartyurl ...]")
            return

        projects = [Project.get(arg) for arg in args.projects]

        for project in projects:
            print(f"Scraping {project}")
            project.getItems()

            print(f"Fetching {len(project.items)} item headers")

            urlitems = []
            with tqdm(total=len(project.items), unit="") as t:
                async for (urlitem, e) in project.fetchAllMetadata():
                    t.update()
                    if e is not None:
                        if isinstance(e, ClientResponseError):
                            tqdm.write(f"{e.status} failed to download {e.request_info.url}")
                        continue
                    urlitems.append(urlitem)

            print(f"Downloading {len(urlitems)} items")

            with tqdm(total=sum(i.size for i in urlitems), unit="bytes", unit_scale=True) as t:
                async for (urlitem, e) in UrlItem.downloadAll(urlitems, args.update):
                    t.update(urlitem.size)
                    if e is not None:
                        if isinstance(e, ClientResponseError):
                            tqdm.write(f"{e.status} failed to download {e.request_info.url}")
                        continue

        print("\n"
              "All projects done!\n"
              "\n"
              "Enjoy ;)")
    except (YiffException, HTTPError) as e:
        print(e, file=sys.stderr)


def main():
    loop = asyncio.get_event_loop()
    loop.run_until_complete(scrape())
    loop.close()


# Main program
if __name__ == "__main__":
    main()
