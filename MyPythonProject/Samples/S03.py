# -*- coding: utf-8 -*-
from Applications.Database.DigitalAudioFiles.shared import select
from Applications.shared import UTF8
from logging.config import dictConfig
import logging
import yaml
import os

__author__ = 'Xavier ROSSET'


with open(os.path.join(os.path.expandvars("%_COMPUTING%"), "logging.yml"), encoding=UTF8) as fp:
    dictConfig(yaml.load(fp))
logger = logging.getLogger(os.path.splitext(os.path.basename(__file__))[0])
for row in select():
    print(row)
