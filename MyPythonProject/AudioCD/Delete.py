# -*- coding: utf-8 -*-
import os
import re
import sys
import yaml
import logging
from logging.config import dictConfig
from Applications.shared import DATABASE, interface
from Applications.parsers import deleterippinglog
from Applications.Database.AudioCD.shared import deletefromuid

__author__ = 'Xavier ROSSET'


# ========
# Classes.
# ========
class Interface(object):

    _regex = re.compile(r"\d+")
    _inputs = [("Enter database to update", "database"),
               ("Singled or Ranged ", "type"),
               ("Enter interface(s) unique ID", "uid"),
               ("Enter ranged from interface unique ID", "from_uid"),
               ("Enter ranged to interface unique ID", "to_uid")]

    def __init__(self):
        self._index, self._step = 0, 0
        self._database = None
        self._type = None
        self._uid = None
        self._from_uid = None
        self._to_uid = None
        self._arguments = []

    def __iter__(self):
        return self

    def __next__(self):
        if self._index >= len(self._inputs):
            raise StopIteration
        if self._uid:
            raise StopIteration
        self._index += 1
        self._step += 1
        return self._inputs[self._index - 1]

    # -----
    # STEP.
    # -----
    @property
    def step(self):
        return self._step

    # ----------
    # ARGUMENTS.
    # ----------
    @property
    def arguments(self):
        return self._arguments

    # ---------
    # DATABASE.
    # ---------
    @property
    def database(self):
        return self._database

    @database.setter
    def database(self, arg):
        val = DATABASE
        if arg:
            arg = arg.replace('"', '')
        if arg and not(os.path.exists(arg) and os.path.isfile(arg)):
            raise ValueError('"{0}" isn\'t a valid database.'.format(arg))
        elif arg and os.path.exists(arg) and os.path.isfile(arg):
            val = arg
        self._database = val
        self._arguments.extend(["--db", val])

    # -----
    # TYPE.
    # -----
    @property
    def type(self):
        return self._type

    @type.setter
    def type(self, arg):
        if arg.upper() not in ["R", "S"]:
            raise ValueError('"{0}" isn\'t a valid choice.'.format(arg))
        self._type = arg.upper()
        if arg.upper() == "S":
            self._arguments.extend(["singled"])
        elif arg.upper() == "R":
            self._arguments.extend(["ranged"])
            self._index = 3

    # ----
    # UID.
    # ----
    @property
    def uid(self):
        return self._uid

    @uid.setter
    def uid(self, arg):
        if not arg:
            raise ValueError('Please enter interface(s) unique ID.')
        arg = self._regex.findall(arg)
        if not arg:
            raise ValueError('Please enter coherent interface(s) unique ID.')
        self._uid = arg
        self._arguments.extend(arg)
        # raise StopIteration

    # ---------
    # FROM_UID.
    # ---------
    @property
    def from_uid(self):
        return self._from_uid

    @from_uid.setter
    def from_uid(self, arg):
        if not arg:
            raise ValueError('Please enter ranged from UID.')
        match = self._regex.match(arg)
        if not match:
            raise ValueError('Please enter coherent ranged from UID.')
        self._from_uid = arg
        self._arguments.append(arg)

    # -------
    # TO_UID.
    # -------
    @property
    def to_uid(self):
        return self._to_uid

    @to_uid.setter
    def to_uid(self, arg):
        val = "9999"
        if arg:
            match = self._regex.match(arg)
            if not match:
                raise ValueError('Please enter coherent ranged to UID.')
            self._to_uid = arg
            val = arg
        self._arguments.append(val)


# ===============
# Main algorithm.
# ===============
if __name__ == "__main__":

    with open(os.path.join(os.path.expandvars("%_COMPUTING%"), "logging.yml"), encoding="UTF_8") as fp:
        dictConfig(yaml.load(fp))
    logger = logging.getLogger("Default.{0}".format(os.path.splitext(os.path.basename(__file__))[0]))

    # --> User interface.
    gui = interface(Interface())

    # --> Parse arguments.
    arguments = deleterippinglog.parse_args(gui.arguments)

    # --> Log arguments.
    logger.debug(arguments.uid)
    logger.debug(arguments.database)

    # --> Delete interfaces.
    sys.exit(deletefromuid(*arguments.uid, db=arguments.database))
