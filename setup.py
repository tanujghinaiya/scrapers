from setuptools import setup

setup(
    name="scrapers",
    packages=["main", "comm", "scrapers", "tasks"],
    entry_points={
        "console_scripts": [
        ]
    },
    install_requires=[
        "lxml",
        "requests",
        "beautifulsoup4"
    ]
)
