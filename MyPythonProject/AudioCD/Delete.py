# -*- coding: utf-8 -*-
import os
import sys
import yaml
import logging
from logging.config import dictConfig
from Applications.parsers import deleterippinglog
from Applications.Database.AudioCD.shared import deletefromuid

__author__ = 'Xavier ROSSET'


# ========
# Logging.
# ========
with open(os.path.join(os.path.expandvars("%_COMPUTING%"), "logging.yml"), encoding="UTF_8") as fp:
    dictConfig(yaml.load(fp))
logger = logging.getLogger("Default.{0}".format(os.path.splitext(os.path.basename(__file__))[0]))


# ================
# Initializations.
# ================
arguments = deleterippinglog.parse_args()


# ===============
# Main algorithm.
# ===============
logger.debug(arguments.uid)
logger.debug(arguments.database)
sys.exit(deletefromuid(*arguments.uid, db=arguments.database))
