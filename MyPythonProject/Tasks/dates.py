# -*- coding: utf-8 -*-
import os
import yaml
import logging
from logging.config import dictConfig
from Applications.parsers import readtable
from Applications.Database.Tables.shared import select
from Applications.shared import dateformat, LOCAL, UTC, TEMPLATE2

__author__ = 'Xavier ROSSET'


# ========
# Logging.
# ========
with open(os.path.join(os.path.expandvars("%_COMPUTING%"), "logging.yml"), encoding="UTF_8") as fp:
    dictConfig(yaml.load(fp))
logger = logging.getLogger("Applications.Database.Tables")


# ==========
# Arguments.
# ==========
arguments = readtable.parse_args()


# ===============
# Main algorithm.
# ===============
for record in select(arguments.table, db=arguments.database):
    if record:
        uid, date = record
        print("\n-*- {0} -*-".format(uid))
        # print(dateformat(UTC.localize(date), TEMPLATE2))
        print(dateformat(UTC.localize(date).astimezone(LOCAL), TEMPLATE2))
