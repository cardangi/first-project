# -*- coding: utf-8 -*-
import os
import re
import sys
import argparse
from Applications.shared import validdb
from Applications.Database.AudioCD.shared import deletefromuid

__author__ = 'Xavier ROSSET'


lass SetExtensions(argparse.Action):
    """
    Set "uid" attribute.
    """
    rex1, rex2 = re.compile(r"\d(?:\d(?:\d(?:\d)?)?)?"), re.compile(r"^({0})\b\s?-\s?\b({0})$".format(digits))
  
    def __init__(self, option_strings, dest, **kwargs):
        super(SetExtensions, self).__init__(option_strings, dest, **kwargs)

    def __call__(self, parsobj, namespace, values, option_string=None):
        setattr(namespace, self.dest, values)
        
        # Ranged Unique ID.
        match = self.rex2.match(values)
        if match:
            setattr(namespace, "uid", list(range(int(match.group(1)), int(match.group(2)) + 1)))

        # Singled Unique ID.
        uid = self.rex1.findall(values)
        if uid:
            setattr(namespace, "uid", list(map(int, uid)))


# =================
# Arguments parser.
# =================
parser = argparse.ArgumentParser()
parser.add_argument("input", action=GetUID)
parser.add_argument("-d", "--db", dest="database", default=os.path.join(os.path.expandvars("%_COMPUTING%"), "database.db"), type=validdb)


# ================
# Initializations.
# ================
arguments = parser.parse_args()


# ===============
# Main algorithm.
# ===============
sys.exit(deletefromuid(*arguments.uid, db=arguments.database))
