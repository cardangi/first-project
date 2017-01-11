# -*- coding: utf-8 -*-
import os
import sys
import yaml
import logging
from logging.config import dictConfig
from Applications.shared import interface, GlobalInterface
from Applications.parsers import deleterippinglog
from Applications.Database.AudioCD.shared import deletefromuid
from Applications.descriptors import Answers, Database, Integer

__author__ = 'Xavier ROSSET'


# ========
# Classes.
# ========
class LocalInterface(GlobalInterface):

    # Data descriptor(s).
    database = Database()
    mode = Answers("S", "R", default="S")
    uid = Integer()
    from_uid = Integer()
    to_uid = Integer(mandatory=False, default="9999")

    # Instance method(s).
    def __init__(self, *args):
        super(LocalInterface, self).__init__(*args)


# ===============
# Main algorithm.
# ===============
if __name__ == "__main__":

    # --> Logging interface.
    with open(os.path.join(os.path.expandvars("%_COMPUTING%"), "logging.yml"), encoding="UTF_8") as fp:
        dictConfig(yaml.load(fp))
    logger = logging.getLogger("Applications.Database.AudioCD")

    # --> Initializations.
    arguments = []

    # --> User interface.
    gui = interface(LocalInterface([("Please enter database to update", "database"), ("Would you to update singled or ranged records? [S/R]", "mode")],
                                   {"S": [("Please enter record(s) unique ID", "uid")], "R": [("Please enter ranged from record unique ID", "from_uid"), ("Please enter ranged to record unique ID", "to_uid")]}
                                   )
                    )

    # --> Parse arguments.
    arguments.extend(["--db", gui.database])
    if gui.mode == "S":
        arguments.append("singled")
        arguments.extend(gui.uid)
    elif gui.mode == "R":
        arguments.append("ranged")
        arguments.extend(gui.from_uid)
        arguments.extend(gui.to_uid)
    arguments = deleterippinglog.parse_args(arguments)

    # --> Log arguments.
    logger.debug(arguments.database)
    logger.debug(arguments.uid)

    # --> Delete record(s).
    sys.exit(deletefromuid(*arguments.uid, db=arguments.database))
