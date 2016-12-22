# -*- coding: utf-8 -*-
import os
import sys
import yaml
import logging
from logging.config import dictConfig
from Applications.shared import interface
from Applications.parsers import deleterippinglog
from Applications.descriptors import Answers, Database, Integer
from Applications.Database.AudioCD.shared import deletefromuid

__author__ = 'Xavier ROSSET'


# ========
# Classes.
# ========
class Interface(object):

    # Data descriptor(s).
    database = Database()
    mode = Answers("S", "R", default="S")
    uid = Integer()
    from_uid = Integer()
    to_uid = Integer(mandatory=False, default="9999")

    # Class variable(s).
    _inputs = [("Please enter database to update", "database"),
               ("Would you to update singled or ranged records? [S/R]", "mode"),
               ("Please enter record(s) unique ID", "uid"),
               ("Please enter ranged from record unique ID", "from_uid"),
               ("Please enter ranged to record unique ID", "to_uid")]

    def __init__(self):
        self._index = 0
        self._step = 0

    def __iter__(self):
        return self

    def __next__(self):
        if self._index >= len(self._inputs):
            raise StopIteration
        # if self.uid:
        #     raise StopIteration
        self._index += 1
        self._step += 1
        return self._inputs[self._index - 1]

    @property
    def step(self):
        return self._step


# ===============
# Main algorithm.
# ===============
if __name__ == "__main__":

    # --> Logging interface.
    with open(os.path.join(os.path.expandvars("%_COMPUTING%"), "logging.yml"), encoding="UTF_8") as fp:
        dictConfig(yaml.load(fp))
    logger = logging.getLogger("Default.{0}".format(os.path.splitext(os.path.basename(__file__))[0]))

    # --> Initializations.
    arguments = []

    # --> User interface.
    gui = interface(Interface())

    # --> Parse arguments.
    arguments.extend(["--db", gui.database])
    if gui.mode == "S":
        arguments.append("singled")
        arguments.extend(gui.uid)
    elif gui.mode == "R":
        arguments.append("ranged")
        arguments.extend(gui.from_uid)
        arguments.extend(gui.to_uid)

    # --> Parse arguments.
    arguments = deleterippinglog.parse_args(arguments)

    # --> Log arguments.
    logger.debug(arguments.database)
    logger.debug(arguments.uid)

    # --> Delete record(s).
    sys.exit(0)
    sys.exit(deletefromuid(*arguments.uid, db=arguments.database))
