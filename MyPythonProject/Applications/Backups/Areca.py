# -*- coding: ISO-8859-1 -*-
__author__ = 'Xavier ROSSET'


# =================
# Absolute imports.
# =================
import os
import sys
import logging
import argparse
import operator
import subprocess
from pytz import timezone
from string import Template
from itertools import repeat
from datetime import datetime
import xml.etree.ElementTree as ET
from os.path import exists, expandvars, join, normpath


# =================
# Relative imports.
# =================
from .. import shared


# ==========
# Functions.
# ==========
def validworkspace(s):
    if s not in ["documents", "miscellaneous", "music", "pictures", "videos"]:
        raise argparse.ArgumentTypeError('"{0}" is not a valid workspace'.format(s))
    return s


# =================
# Arguments parser.
# =================
parser = argparse.ArgumentParser()
parser.add_argument("workspace", type=validworkspace)
parser.add_argument("target", nargs="+")
parser.add_argument("--full", action="store_true")
parser.add_argument("--check", action="store_true")
parser.add_argument("--debug", action="store_true")


# ==========
# Constants.
# ==========
BACKUP, TEMP = expandvars("%_BACKUP%"), expandvars("%TEMP%")


# ==========
# Templates.
# ==========
t1 = Template("$command $full")
t2 = Template("$command $check")
t3 = Template(r'$command -wdir "$temp\tmp-Xavier" -config "$config"')


# ========
# Logging.
# ========
logger = logging.getLogger("%s.%s" % (__package__, os.path.basename(__file__)))


# ================
# Initializations.
# ================
returncode, arguments = [], parser.parse_args()


# ==============
# Log arguments.
# ==============
logger.info("{0} {1} {0}".format("".join(list(repeat("=", 50))), shared.dateformat(datetime.now(tz=timezone(shared.DFTTIMEZONE)), shared.TEMPLATE1)))
logger.info('START "%s".' % (os.path.basename(__file__),))
if arguments.debug:
    logger.debug("Workspace.")
    logger.debug('\t"%s".'.expandtabs(4) % (arguments.workspace,))
    logger.debug("Target(s).")
    for target in arguments.target:
        logger.debug('\t"%s".'.expandtabs(4) % (target,))


# ===============
# Main algorithm.
# ===============
for target in arguments.target:

    cfgfile = join(BACKUP, "workspace.%s" % (arguments.workspace,), "%s.bcfg" % (target,))
    if not exists(cfgfile):
        if arguments.debug:
            logger.debug("Warning.")
            logger.debug('\t"{0}" doesn\'t exist: backup can\'t be processed.'.format(cfgfile).expandtabs(4))
        continue

    root = ET.parse(cfgfile).getroot()
    directory = normpath(root.find("medium").get("path"))
    if arguments.debug:
        logger.debug("Destination directory.")
        logger.debug('\t"%s".'.expandtabs(4) % (directory,))
    if not exists(directory):
        if arguments.debug:
            logger.debug("Warning.")
            logger.debug('\t"{0}" doesn\'t exist: backup can\'t be processed.'.format(directory).expandtabs(4))
        continue

    command = shared.ARECA + " backup"
    if arguments.full:
        command = t1.substitute(command=command, full="-f")
    if arguments.check:
        command = t2.substitute(command=command, check="-c")
    args = t3.substitute(command=command, temp=TEMP, config=cfgfile)
    if arguments.debug:
        logger.debug("Backup command.")
        logger.debug('\t%s.'.expandtabs(4) % (args,))
    process = subprocess.run(args, stdout=subprocess.PIPE, universal_newlines=True)
    returncode.append(process.returncode)
    if process.returncode:
        if arguments.debug:
            logger.debug("Warning.")
            logger.debug('\t"{0}" was returned by "areca_cl.exe". Backup failed.'.format(process.returncode).expandtabs(4))
        continue

    logger.info("Areca backup log.")
    for line in process.stdout.splitlines():
        logger.info("\t%s".expandtabs(4) % (line,))


# =============
# Stop logging.
# =============
logger.info('END "%s".' % (os.path.basename(__file__),))


# ===============
# Exit algorithm.
# ===============
if all(not operator.eq(i, 0) for i in returncode):
    sys.exit(99)
if any(operator.eq(i, 0) for i in returncode):
    sys.exit(0)


# Fix areca backup
# Fix areca backup
# Fix areca backup
# Fix areca backup
