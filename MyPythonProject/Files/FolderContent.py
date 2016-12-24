# -*- coding: utf-8 -*-
import os
import sys
import yaml
import json
import logging
import argparse
from logging.config import dictConfig
from Applications.parsers import foldercontent
from Applications.descriptors import Answers, Folder, Extensions
from Applications.shared import interface, filesinfolder, UTF8, WRITE

__author__ = "Xavier ROSSET"


# ========
# Classes.
# ========
class LocalInterface(object):

    folder = Folder()
    extensions = Extensions()
    json_output = Answers("N", "Y", default="Y")

    # Instance method(s).
    def __init__(self, *args):
        self._name = None
        self._args = args
        self._levels = 2
        self._level = 0
        self._step = 0

    def __iter__(self):
        return self

    def __next__(self):

        # Stop iteration once second level is exhausted.
        if self._level >= self._levels and self._index >= len(self._inputs):
            raise StopIteration

        # Stop iteration once first level is exhausted with not "Y" as answer.
        if self._level == 1 and self._index >= len(self._inputs) and self.json_output != "Y":
            raise StopIteration

        # Load second level once first level is exhausted with "Y" as answer.
        if self._level == 1 and self._index >= len(self._inputs) and self.json_output == "Y":
            self._inputs = list(self._args[self._level])
            self._level += 1
            self._index = 0

        # Load first level.
        elif self._level == 0:
            self._inputs = list(self._args[self._level])
            self._level += 1
            self._index = 0

        self._index += 1
        self._step += 1
        return self._inputs[self._index - 1]

    # Properties.
    @property
    def step(self):
        return self._step

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, arg):
        if not arg:
            arg = os.path.join(os.path.expandvars("%TEMP%"), "content.json")
        if not os.path.exists(os.path.dirname(arg)):
            raise ValueError('"{0}" doesn\'t exist. Please enter an existing directory'.format(os.path.dirname(arg)))
        self._name = arg


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
    gui = interface(LocalInterface([("Please enter folder", "folder"), ("Please enter extension(s)", "extensions"), ("Would you like to display content in a JSON file [Y/N]?", "json_output")],
                                   [("Please enter JSON file name", "name")]))

    # --> Define new argument.
    foldercontent.add_argument("--json", dest="output", default=os.path.join(os.path.expandvars("%TEMP%"), "content.txt"), type=argparse.FileType(mode=WRITE, encoding=UTF8))

    # --> Parse arguments.
    arguments.append(gui.folder)
    arguments.extend(gui.extensions)
    if gui.json_output == "Y":
        arguments.append("--json")
        arguments.append(gui.name)
    arguments = foldercontent.parse_args(arguments)

    # --> Log arguments.
    logger.debug(arguments.folder)
    logger.debug(arguments.extensions)
    logger.debug(gui.json_output)

    # --> Main algorithm.

    # -->  1. Default JSON output.
    if gui.json_output == "Y":
        json.dump(sorted(sorted(filesinfolder(*arguments.extensions, folder=arguments.folder)), key=lambda i: os.path.splitext(i)[1][1:]), arguments.output, indent=4, ensure_ascii=False)
        sys.exit(0)

    # -->  2. Text output.
    for num, file in enumerate(sorted(sorted(filesinfolder(*arguments.extensions, folder=arguments.folder)), key=lambda i: os.path.splitext(i)[1][1:]), start=1):
        arguments.output.write("{0:>3d}. {1}\n".format(num, os.path.normpath(file)))
    sys.exit(0)
