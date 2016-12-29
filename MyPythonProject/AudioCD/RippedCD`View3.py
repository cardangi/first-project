# -*- coding: utf-8 -*-
from Applications.Database.AudioCD.shared import select
from logging.config import dictConfig
from Applications.shared import UTF8
import yaml
import os

__author__ = 'Xavier ROSSET'


# ========
# Logging.
# ========
with open(os.path.join(os.path.expandvars("%_COMPUTING%"), "logging.yml"), encoding=UTF8) as fp:
    dictConfig(yaml.load(fp))


# ===============
# Main algorithm.
# ===============
for row in select():
    print(row)
