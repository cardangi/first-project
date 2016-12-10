# -*- coding: utf-8 -*-
import os
from Applications.parsers import foldercontent
from Applications.shared import filesinfolder, UTF8, WRITE

__author__ = "Xavier ROSSET"


# ==========
# Arguments.
# ==========
arguments = foldercontent.parse_args()


# ===============
# Main algorithm.
# ===============
with open(os.path.join(os.path.expandvars("%TEMP%"), "content.txt"), mode=WRITE, encoding=UTF8) as fp:
    for num, file in enumerate(sorted(sorted(filesinfolder(*arguments.extensions, folder=arguments.folder)), key=lambda i: os.path.splitext(i)[1][1:]), start=1):
        fp.write("{0:>3d}. {1}\n".format(num, os.path.normpath(file)))
