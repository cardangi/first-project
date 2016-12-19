# -*- utf-8 -*-
import os
import yaml
import logging
from logging.config import dictConfig
from Applications.shared import filesinfolder, IMAGES

__author__ = 'Xavier ROSSET'


with open(os.path.join(os.path.expandvars("%_COMPUTING%"), "logging.yml"), encoding="UTF_8") as fp:
    dictConfig(yaml.load(fp))
logger = logging.getLogger("Default.{0}".format(os.path.splitext(os.path.basename(__file__))[0]))
for file in filesinfolder("jpg", folder=IMAGES, excluded=["Recover", "iPhone", "Recycle", "\$Recycle"]):
    logger.debug(file)
