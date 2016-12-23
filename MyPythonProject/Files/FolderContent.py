# -*- coding: utf-8 -*-
import os
import yaml
import logging
from logging.config import dictConfig
from Applications.parsers import foldercontent
from Applications.descriptors import Folder, Extensions
from Applications.shared import interface, filesinfolder, UTF8, WRITE, GlobalInterface

__author__ = "Xavier ROSSET"


# ========
# Classes.
# ========
class LocalInterface(GlobalInterface):

    folder = Folder()
    extensions = Extensions()

    def __init__(self, *args):
        super(LocalInterface, self).__init__(*args)


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
    gui = interface(LocalInterface(("Please enter folder", "folder"), ("Please enter extension(s)", "extensions")))

    # --> Parse arguments.
    arguments.append(gui.folder)
    arguments.extend(gui.extensions)
    arguments = foldercontent.parse_args(arguments)

    # --> Log arguments.
    logger.debug(arguments.folder)
    logger.debug(arguments.extensions)

    # --> Main algorithm.
    with open(os.path.join(os.path.expandvars("%TEMP%"), "content.txt"), mode=WRITE, encoding=UTF8) as fp:
        for num, file in enumerate(sorted(sorted(filesinfolder(*arguments.extensions, folder=arguments.folder)), key=lambda i: os.path.splitext(i)[1][1:]), start=1):
            fp.write("{0:>3d}. {1}\n".format(num, os.path.normpath(file)))
