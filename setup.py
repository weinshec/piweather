#!/usr/bin/env python

from pathlib import Path
from setuptools import setup


root = Path(__file__).parent or "."

with (root / "README.rst").open(encoding="utf-8") as f:
    long_description = f.read()

with (root / "requirements.txt").open(encoding="utf-8") as f:
    requirements = list(filter(None, (row.strip() for row in f)))

info = {
    "name":                "piweather",
    "version":             "0.1",
    "author":              "Christoph Weinsheimer",
    "author_email":        "ch.weinsheimer@googlemail.com",
    "url":                 "https://github.com/weinshec/piweather",
    "packages":            ["piweather"],
    "provides":            ["piweather"],
    "description":         "Automatic weather station based on python and a Raspberry Pi",
    "long_description":    long_description,
    "keywords":            ["raspberrypi", "python", "aws", "weather"],
    "install_requires":    requirements,
    "setup_requires":      ["nose", "flake8", "coverage"],
}

if __name__ == "__main__":
    setup(**info)
