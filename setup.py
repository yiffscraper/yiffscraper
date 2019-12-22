import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

requirements = []
with open('requirements.txt') as f:
    requirements = f.read().splitlines()

setuptools.setup(
    name="yiffscraper",
    version="1.0.0",
    author="Natalie Fearnley",
    author_email="nfearnley@gmail.com",
    description="Scrapes off all content from a yiff.party page",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yiffscraper/yiffscraper",
    python_requires=">=3.5",
    install_requires=requirements,
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3.5",
        "Operating System :: OS Independent",
        "License :: OSI Approved :: MIT License"
    ],
    entry_points={
        "console_scripts": [
            "yiffx=yiffscraper.__main__:main"
        ]
    }
)
