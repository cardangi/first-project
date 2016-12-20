# -*- coding: utf-8 -*-
import os
import re
import yaml
import logging
from logging.config import dictConfig
from Applications.parsers import foldercontent
from Applications.shared import interface, filesinfolder, UTF8, WRITE

__author__ = "Xavier ROSSET"


# ========
# Classes.
# ========
class Interface(object):

    _regex = re.compile(r"\W+")
    _inputs = [("Please enter folder", "folder"), ("Please enter extension(s)", "extensions")]

    def __init__(self):
        self._index, self._step = 0, 0
        self._folder = None
        self._extensions = None
        self._arguments = []

    def __iter__(self):
        return self

    def __next__(self):
        if self._index >= len(self._inputs):
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

    # -------
    # FOLDER.
    # -------
    @property
    def folder(self):
        return self._folder

    @folder.setter
    def folder(self, arg):
        if arg:
            arg = arg.replace('"', '')
        if not os.path.exists(arg):
            raise ValueError('"{0}" isn\'t a valid folder.'.format(arg))
        self._folder = arg
        self._arguments.append(arg)

    # -----------
    # EXTENSIONS.
    # -----------
    @property
    def extensions(self):
        return self._extensions

    @extensions.setter
    def extensions(self, arg):
        if arg:
            self._extensions = arg
            self._arguments.extend(self._regex.split(arg))


# ===============
# Main algorithm.
# ===============
if __name__ == "__main__":

    # --> Logging interface.
    with open(os.path.join(os.path.expandvars("%_COMPUTING%"), "logging.yml"), encoding="UTF_8") as fp:
        dictConfig(yaml.load(fp))
    logger = logging.getLogger("Default.{0}".format(os.path.splitext(os.path.basename(__file__))[0]))

    # --> User interface.
    gui = interface(Interface())

    # --> Parse arguments.
    arguments = foldercontent.parse_args(gui.arguments)

    # --> Log arguments.
    logger.debug(arguments.folder)
    logger.debug(arguments.extensions)

    # --> Main algorithm.
    with open(os.path.join(os.path.expandvars("%TEMP%"), "content.txt"), mode=WRITE, encoding=UTF8) as fp:
        for num, file in enumerate(sorted(sorted(filesinfolder(*arguments.extensions, folder=arguments.folder)), key=lambda i: os.path.splitext(i)[1][1:]), start=1):
            fp.write("{0:>3d}. {1}\n".format(num, os.path.normpath(file)))
