# -*- coding: utf-8 -*-
import os
import yaml
import logging
from itertools import groupby
from operator import itemgetter
from logging.config import dictConfig

__author__ = 'Xavier ROSSET'


# ========
# Logging.
# ========
with open(os.path.join(os.path.expandvars("%_COMPUTING%"), "logging.yml"), encoding="UTF_8") as fp:
    dictConfig(yaml.load(fp))
logger = logging.getLogger("{0}".format(os.path.splitext(os.path.basename(__file__))[0]))


# ===============
# Main algorithm.
# ===============
mylist = (("2014", "AB"), ("2010", "A"), ("2013", "B"), ("2010", "C"), ("2016", "D"), ("2015", "E"), ("2010", "F"), ("2016", "G"), ("2012", "H"), ("2012", "I"), ("2010", "J"), ("2014", "AA"),
          ("2015", "K"))
for k, v in groupby(sorted(sorted(mylist, key=itemgetter(1)), key=lambda i: int(i[0])), key=lambda i: int(i[0])):
    logger.debug("{0}: {1}".format(k, sorted([itemgetter(1)(item) for item in v])))
