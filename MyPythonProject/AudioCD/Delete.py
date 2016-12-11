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

    inputs = {"1": ("Enter database to update", "database"),
              "2": ("Singled or Ranged ", "type"),
              "3": ("Enter record(s) unique ID", "uid"),
              "4": ("Enter from", "min"),
              "5": ("Enter to", "max")}

    def __init__(self):
        self._index, self._step = None, 0

    def __call__(self, *args, **kwargs):
        self._step += 1
        return self.inputs[str(self.index)]

    @property
    def index(self):
        return self._index

    @index.setter
    def index(self, arg):
        self._index = arg

    @property
    def step(self):
        return self._step


# ================
# Initializations.
# ================
regex1, args = re.compile(r"\d+"), []


# ===============
# Main algorithm.
# ===============
if __name__ == "__main__":

    with open(os.path.join(os.path.expandvars("%_COMPUTING%"), "logging.yml"), encoding="UTF_8") as fp:
        dictConfig(yaml.load(fp))
    logger = logging.getLogger("Default.{0}".format(os.path.splitext(os.path.basename(__file__))[0]))

    choice, record = None, RippingLog()
    record.index = 0
    while True:
        try:
            record.index += 1
            inp, fld = record()
            while True:
                choice = input("{0}. {1}: ".format(record.step, inp))

                if fld == "database":
                    if choice:
                        choice = choice.replace('"', '')
                    if choice and not(os.path.exists(choice) and os.path.isfile(choice)):
                        continue
                    elif choice and os.path.exists(choice) and os.path.isfile(choice):
                        args.extend(["--db", choice])
                        break
                    args.extend(["--db", DATABASE])
                    break

                elif fld == "type":
                    if choice not in ["R", "S"]:
                        continue
                    if choice.upper() == "S":
                        args.extend(["singled"])
                    elif choice.upper() == "R":
                        args.extend(["ranged"])
                        record.index += 1
                    break

                elif fld == "uid":
                    if not choice:
                        continue
                    choice = regex1.findall(choice)
                    if not choice:
                        continue
                    args.extend(choice)
                    break

                elif fld == "min":
                    if not choice:
                        continue
                    match = regex1.match(choice)
                    if not match:
                        continue
                    args.append(choice)
                    break

                elif fld == "max":
                    if choice:
                        match = regex1.match(choice)
                        if not match:
                            continue
                        args.append(choice)
                    break

            if fld == "uid":
                break

        except KeyError:
            break

    # --> Parse arguments.
    arguments = deleterippinglog.parse_args(args)

    # --> Log arguments.
    logger.debug(arguments.uid)
    logger.debug(arguments.database)

    # --> Delete records.
    sys.exit(deletefromuid(*arguments.uid, db=arguments.database))
