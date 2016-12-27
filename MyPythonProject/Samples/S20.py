# -*- coding: utf-8 -*-
import sys
from Applications.parsers import readtable
from Applications.Database.Tables.shared import isdeltareached

__author__ = 'Xavier ROSSET'


# ==========
# Constants.
# ==========
MAPPING = {False: 1, True: 0}


# ==========
# Arguments.
# ==========
readtable.add_argument("-d", "--delta", help="delta required to trigger action(s)", nargs="?", default="10", const="10", type=int)
arguments = readtable.parse_args()


# ===============
# Main algorithm.
# ===============
deltareached = MAPPING[isdeltareached(arguments.uid, arguments.table, arguments.database, arguments.delta)]
print(deltareached)
sys.exit(deltareached)
