# -*- coding: utf-8 -*-
from Applications.Database.AudioCD.shared import select
from logging.config import dictConfig
from Applications.shared import UTF8
import argparse
import yaml
import os

__author__ = 'Xavier ROSSET'


# ==========
# Functions.
# ==========
def validdb(arg):
    if not os.path.exists(arg):
        raise argparse.ArgumentTypeError('"{0}" doesn\'t exist.'.format(arg))
    return arg


# ========
# Logging.
# ========
with open(os.path.join(os.path.expandvars("%_COMPUTING%"), "logging.yml"), encoding=UTF8) as fp:
    dictConfig(yaml.load(fp))


# =================
# Arguments parser.
# =================
parser = argparse.ArgumentParser()
parser.add_argument("database", nargs="?", default=os.path.join(os.path.expandvars("%_COMPUTING%"), "database.db"), type=validdb)


# ================
# Initializations.
# ================
arguments = parser.parse_args()


# ===============
# Main algorithm.
# ===============
for row in select(db=arguments.database):
    print(row)
