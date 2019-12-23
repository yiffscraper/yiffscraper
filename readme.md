# Yiffscraper

Scrapes off all content from a yiff.party page

## Getting Started

These instructions will get you a copy of yiffscraper installed and running on your machine.

### Requirements

* [Python 3.6+](https://www.python.org/downloads/release)
* [beautifulsoup4](https://pypi.org/project/beautifulsoup4/)
* [requests](https://pypi.org/project/requests/)
* [tqdm](https://pypi.org/project/tqdm/)
* [aiohttp](https://pypi.org/project/aiohttp/)
* [python-dateutil](https://pypi.org/project/python-dateutil/)

### Installing

Make sure you have Python 3.6+ installed before proceeding.

```
pip install yiffscraper
```

### Running

Once it is installed, you should be able to run the program by typing `yiff` on the command line.

yiffscraper accepts a Patreon id, or a yiff.party url, or a Patreon url.
```
yiff 7236857
yiff https://yiff.party/patreon/7236857
yiff https://www.patreon.com/ericaofanderson
```

yiffscraper will also accept multiple arguments to download several projects at once.
```
yiff https://www.patreon.com/ericaofanderson https://yiff.party/patreon/13240009
```

yiffscraper will download all project files into a "scrapes" directory wherever it is run.

If called with the --update argument, yiffscraper will download any new or updated content, and ignore any content that has already been downloaded.

```
yiff 7236857 --update
```

## Authors

* **[shubham418](https://github.com/shubham418)** - *Original [YiffScraper](https://github.com/shubham418/yiff_scraper)*
* **[LaChocola](https://github.com/LaChocola)** - *Update Project Manager*
* **[DigiDuncan](https://github.com/DigiDuncan)** - *Update Coder*
* **[Natalie Fearnley](https://github.com/nfearnley)** - *Bug fixer*

See also the list of [contributors](https://github.com/yiffscraper/yiffscraper/contributors) who participated in this project.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details
