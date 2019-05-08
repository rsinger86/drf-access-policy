#!/usr/bin/env python
from distutils.core import setup
from codecs import open
from os import path


def readme():
    with open("README.txt", "r") as infile:
        return infile.read()


classifiers = [
    # Pick your license as you wish (should match "license" above)
    "Development Status :: 4 - Beta",
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python :: 3.3",
    "Programming Language :: Python :: 3.4",
    "Programming Language :: Python :: 3.5",
    "Programming Language :: Python :: 3.6",
]
setup(
    name="drf-access-policy",
    version="0.2.0",
    description="Declarative access policies/permissions modeled after AWS' IAM policies.",
    author="Robert Singer",
    author_email="robertgsinger@gmail.com",
    packages=["rest_access_policy"],
    url="https://github.com/rsinger86/drf-access-policy",
    license="MIT",
    keywords="django restframework drf access policy authorization declaritive",
    long_description=readme(),
    classifiers=classifiers,
)
