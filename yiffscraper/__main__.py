import sys
import asyncio
from pathlib import Path

from aiohttp import ClientResponseError

from requests.exceptions import HTTPError
from tqdm import tqdm

from .yiffscraper import Project, YiffException


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

            print(f"Downloading {len(project.items)} links")
            tasks = await project.downloadItems(args.update)
            for task in tqdm(asyncio.as_completed(tasks), total=len(tasks), unit="file"):
                try:
                    await task
                except ClientResponseError as e:
                    tqdm.write(f"{e.status} failed to download {e.request_info.url}")

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
