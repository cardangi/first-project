# -*- coding: utf-8 -*-
from Applications.parsers import readtable
from Applications.Database.Tables.shared import selectfromuid
from Applications.shared import dateformat, LOCAL, UTC, TEMPLATE2

__author__ = 'Xavier ROSSET'


# ==========
# Arguments.
# ==========
arguments = readtable.parse_args()


# ===============
# Main algorithm.
# ===============
record = selectfromuid(arguments.uid, arguments.table, db=arguments.database)
if record:
    id, date = record
    print(id)
    print(dateformat(UTC.localize(date), TEMPLATE2))
    print(dateformat(UTC.localize(date).astimezone(LOCAL), TEMPLATE2))
