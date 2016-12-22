# -*- coding: utf-8 -*-
from timeit import timeit

__author__ = "Xavier ROSSET"

imp = """\
import os
from Applications.shared import filesinfolder
"""
print(timeit(stmt='filesinfolder("jpg", folder=r"G:\Vidéos\Samsung S5")', setup='from Applications.shared import filesinfolder', number=1000000))
print(timeit(stmt='sorted(sorted(filesinfolder("jpg", folder=r"G:\Vidéos\Samsung S5")), key=lambda i: os.path.splitext(i)[1][1:])', setup=imp, number=1000000))
