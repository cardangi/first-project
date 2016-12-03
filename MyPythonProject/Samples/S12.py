# -*- coding: utf-8 -*-
from Applications.AudioCD.shared import MonkeyFilesCollection, FLACFilesCollection
from logging.config import dictConfig
import yaml
import os

__author__ = 'Xavier ROSSET'


with open(os.path.join(os.path.expandvars("%_COMPUTING%"), "logging.yml"), encoding="UTF_8") as fp:
    dictConfig(yaml.load(fp))
MonkeyFilesCollection(r"M:\\")(test=True)
FLACFilesCollection(r"M:\\")(test=True)
