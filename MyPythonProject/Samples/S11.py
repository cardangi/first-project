# -*- coding: utf-8 -*-
from Applications.Database.AudioCD.shared import deletefromuid
from Applications.shared import deleterippinglogparser
from logging.config import dictConfig
import logging
import yaml
import sys
import os

__author__ = 'Xavier ROSSET'


# ========
# Logging.
# ========
with open(os.path.join(os.path.expandvars("%_COMPUTING%"), "logging.yml"), encoding="UTF_8") as fp:
    dictConfig(yaml.load(fp))
logger = logging.getLogger("{0}".format(os.path.splitext(os.path.basename(__file__))[0]))


# ================
# Initializations.
# ================
arguments = deleterippinglogparser.parse_args()


# ===============
# Main algorithm.
# ===============
sys.exit(deletefromuid(*arguments.uid))
