# -*- coding: utf-8 -*-
import os
import sys
import json
from ... import shared

__author__ = 'Xavier ROSSET'


# ==========
# Constants.
# ==========
INPUT = os.path.join(os.path.expandvars("%TEMP%"), "rippinglog.json")


# ===============
# Main algorithm.
# ===============
with open(INPUT) as fp:
    for var in json.loads(fp):



# ===============
# Exit algorithm.
# ===============
sys.exit(0)
