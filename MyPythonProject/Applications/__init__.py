# -*- coding: ISO-8859-1 -*-
import os
import yaml
import logging
from logging.config import dictConfig

__author__ = 'Xavier ROSSET'


# Load logging configuration.
with open(os.path.join(os.path.expandvars("%_COMPUTING%"), "logging.yml")) as fp:
    dictConfig(yaml.load(fp))
parent_logger = logging.getLogger(os.path.basename(__file__))
