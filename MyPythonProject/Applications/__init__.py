# -*- coding: ISO-8859-1 -*-
import os
import yaml
import logging
from logging.config import dictConfig

__author__ = 'Xavier ROSSET'


# Load logging configuration.
with open(os.path.join(os.path.expandvars("%_COMPUTING%"), "logging.yml")) as fp:
    d = yaml.load(fp)
if d:
    dictConfig(d)
    if __name__ == "__main__":
        logger = logging.getLogger(os.path.basename(__file__))
    else:
        logger = logging.getLogger(__name__)
