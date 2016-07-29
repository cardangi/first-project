# -*- coding: utf-8 -*-
import os
import sys
import json
from ... import shared
# from collections import MutableMapping
from sortedcontainers import SortedDict

__author__ = 'Xavier ROSSET'


# ==========
# Constants.
# ==========
INPUT = os.path.join(os.path.expandvars("%_COMPUTING%"), "tags.json")


class RippedCD():

    itags = ["artist", "origyear", "year", "album"]

    def __init__(self, **kwargs):
        self.otags = dict()
        for key in kwargs.keys():
            if key in self.itags:
                setattr(self, key, kwargs[key])
                self.otags[key] = kwargs[key]

    def __len__(self):
        return len(self.otags)

    def __getitem__(self, item):
        return self.otags[item]

    def __setitem__(self, key, value):
        self.otags[key] = value

    def __iter__(self):
        return iter(self.otags)

    def __delitem__(self, key):
        del self.otags[key]

    def __repr__(self):
        return repr(self.otags)


# ===============
# Main algorithm.
# ===============
with open(INPUT) as fp:
    for var in json.load(fp):
        rippedcd = RippedCD(**var)
        print(rippedcd)
        # print(type(rippedcd))
        print(str(rippedcd))
        print(str(rippedcd).split(":"))


# ===============
# Exit algorithm.
# ===============
sys.exit(0)
