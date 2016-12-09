# -*- coding: utf-8 -*-
import os
import re
import sys
import yaml
import argparse
from logging.config import dictConfig
from Applications.shared import validdb
from Applications.Database.AudioCD.shared import deletefromuid

__author__ = 'Xavier ROSSET'


# ========
# Classes.
# ========
class SetExtensions(argparse.Action):
    """
    Set "uid" attribute.
    """
    rex1, rex2 = re.compile(r"\d(?:\d(?:\d(?:\d)?)?)?"), re.compile(r"^({0})\b\s?-\s?\b({0})$".format(r"\d(?:\d(?:\d(?:\d)?)?)?"))
  
    def __init__(self, option_strings, dest, **kwargs):
        super(SetExtensions, self).__init__(option_strings, dest, **kwargs)

    def __call__(self, parsobj, namespace, values, option_string=None):
        setattr(namespace, self.dest, values)
        setattr(namespace, "uid", [])
        
        # Ranged Unique ID.
        match = self.rex2.match(values)
        if match:
            setattr(namespace, "uid", list(range(int(match.group(1)), int(match.group(2)) + 1)))
            return

        # Singled Unique ID.
        setattr(namespace, "uid", list(map(int, self.rex1.findall(values))))


# ========
# Logging.
# ========
with open(os.path.join(os.path.expandvars("%_COMPUTING%"), "logging.yml"), encoding="UTF_8") as fp:
    dictConfig(yaml.load(fp))
logger = logging.getLogger("Default.{0}".format(os.path.splitext(os.path.basename(__file__))[0]))


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
logger.debug(arguments.uid)
sys.exit(deletefromuid(*arguments.uid, db=arguments.database))
