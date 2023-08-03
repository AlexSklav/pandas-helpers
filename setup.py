#!/usr/bin/env python
# -*- encoding: utf-8 -*-
from setuptools import setup

import versioneer

setup(name="pandas-helpers",
      version=versioneer.get_version(),
      cmdclass=versioneer.get_cmdclass(),
      description="A helper package for the pandas data-analysis package.",
      keywords="pandas data-analysis",
      author="Christian Fobel",
      author_email="christian@fobel.net",
      url="https://github.com/sci-bots/pandas-helpers",
      license="BSD",
      install_requires=['pandas', 'scipy'],
      packages=['pandas_helpers'])
