#!/usr/bin/env python3
"""
Setup script for The Dying Lands - Hexcrawl Generator
"""

from setuptools import setup, find_packages
import os

# Read the README file
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Read requirements
with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="dying-lands-hexcrawl",
    version="1.0.0",
    author="Mörk Borg Hexcrawl Generator",
    description="A desktop application for generating hexcrawl maps for The Dying Lands campaign",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/dying-lands-hexcrawl",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Games/Entertainment :: Role-Playing",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
    ],
    python_requires=">=3.7",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "dying-lands=src.webview_launcher:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["web/templates/*.html", "web/static/*.css", "web/static/*.js", "data/*"],
    },
    data_files=[
        ("share/dying-lands", ["README.md"]),
    ],
)