# -*- coding: utf-8 -*-
import os
import re
import sys
import yaml
import logging
from logging.config import dictConfig
from Applications.shared import DATABASE
from Applications.parsers import deleterippinglog
from Applications.Database.AudioCD.shared import deletefromuid

__author__ = 'Xavier ROSSET'


# ========
# Classes.
# ========
class RippingLog(object):

    regex = re.compile(r"\d+")
    inputs = {"1": ("Enter database to update", "database"),
              "2": ("Singled or Ranged ", "type"),
              "3": ("Enter record(s) unique ID", "uid"),
              "4": ("Enter ranged from record unique ID", "from_uid"),
              "5": ("Enter ranged to record unique ID", "to_uid")}

    def __init__(self):
        self._index, self._step = None, 0
        self._database = None
        self._type = None
        self._uid = None
        self._from_uid = None
        self._to_uid = None
        self._arguments = []

    def __call__(self, *args, **kwargs):
        self._step += 1
        return self.inputs[str(self._index)]

    # ------
    # INDEX.
    # ------
    @property
    def index(self):
        return self._index

    @index.setter
    def index(self, arg):
        self._index = arg

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
            self._index += 1

    # ----
    # UID.
    # ----
    @property
    def uid(self):
        return self._uid

    @uid.setter
    def uid(self, arg):
        if not arg:
            raise ValueError('Please enter record(s) unique ID.')
        arg = self.regex.findall(arg)
        if not arg:
            raise ValueError('Please enter coherent record(s) unique ID.')
        self._uid = arg
        self._arguments.extend(arg)
        raise StopIteration

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
        match = self.regex.match(arg)
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
            match = self.regex.match(arg)
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

    value, record = None, RippingLog()
    record.index = 0
    while True:

        try:
            record.index += 1
            inp, dest = record()
            while True:
                value = input("{0}. {1}: ".format(record.step, inp))
                try:
                    setattr(record, dest, value)
                except ValueError:
                    continue
                break

        except (StopIteration, KeyError):
            break

    # --> Parse arguments.
    arguments = deleterippinglog.parse_args(record.arguments)

    # --> Log arguments.
    logger.debug(arguments.uid)
    logger.debug(arguments.database)

    # --> Delete records.
    sys.exit(deletefromuid(*arguments.uid, db=arguments.database))
