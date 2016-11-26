# -*- coding: utf-8 -*-
import os
import sys
import yaml
import json
import logging
import argparse
import operator
import subprocess
from string import Template
from operator import itemgetter
from Applications.shared import ARECA
from logging.config import dictConfig
from xml.etree.ElementTree import parse
from os.path import exists, expandvars, join, normpath

__author__ = 'Xavier ROSSET'


# ===============
# Backup targets.
# ===============
with open(os.path.join(os.path.expandvars("%_PYTHONPROJECT%"), "Areca", "Areca.json")) as fp:
    targets = {item["target"]: item["workspace"] for item in json.load(fp)}  # "item" est un dictionnaire.


# ========
# Classes.
# ========
class GetTargets(argparse.Action):

    def __init__(self, option_strings, dest, **kwargs):
        super(GetTargets, self).__init__(option_strings, dest, **kwargs)

    def __call__(self, parsobj, namespace, values, option_string=None):

        # Tous les scripts associés au workspace sont sélectionnés par défaut. 
        setattr(namespace, self.dest, [item for item in sorted(targets) if targets[item] == getattr(namespace, "workspace")])

        # Les scripts n'appartenant pas au workspace sont éliminés si une liste de scripts est reçue par le programme. 
        if values:
            setattr(namespace, self.dest, [item for item in [item for item in values if item in sorted(targets)] if targets[item] == getattr(namespace, "workspace")])


# =================
# Arguments parser.
# =================
parser = argparse.ArgumentParser()
parser.add_argument("workspace", choices=["documents", "miscellaneous", "music", "pictures", "videos"])
parser.add_argument("targets", nargs="*", action=GetTargets)
parser.add_argument("-f", "--full", action="store_true")
parser.add_argument("-c", "--check", action="store_true")
parser.add_argument("-t", "--test", action="store_true")


# ========
# Logging.
# ========
with open(os.path.join(os.path.expandvars("%_COMPUTING%"), "logging.yml"), encoding="UTF_8") as fp:
    dictConfig(yaml.load(fp))
logger = logging.getLogger("Backup.{0}".format(os.path.splitext(os.path.basename(__file__))[0]))


# ==========
# Templates.
# ==========
t1 = Template("$command $full")
t2 = Template("$command $check")
t3 = Template(r'$command -wdir "$temp\tmp-Xavier" -config "$config"')


# ================
# Initializations.
# ================
returncode, arguments = [], parser.parse_args()


# ===============
# Main algorithm.
# ===============


#     --------------------
#  1. Log input arguments.
#     --------------------

# --> 1.a. Targets available in JSON reference file.
logger.debug("Configured targets.")
for target, workspace in sorted(sorted(targets.items(), key=lambda i: int(i[0])), key=itemgetter(1)):
    logger.debug("\t{0}: {1}.".format(target, workspace).expandtabs(4))

# --> 1.b. Targets given by parser.
logger.debug("Processed targets.")
if arguments.targets:
    for target in sorted(arguments.targets, key=int):
        logger.debug("\t{0}.".format(target).expandtabs(4))
elif not arguments.targets:
    logger.debug("\tAny coherent target hasn\'t been given: backup can\'t be processed!".expandtabs(4))


#     ------------------
#  2. Process arguments.
#     ------------------
for target in arguments.targets:

    #  2.a. Get backup configuration file.
    cfgfile = join(expandvars("%_BACKUP%"), "workspace.%s" % (arguments.workspace,), "%s.bcfg" % (target,))
    logger.debug("Configuration file.")
    logger.debug('\t"%s".'.expandtabs(4) % (cfgfile,))
    try:
        assert exists(cfgfile) is True
    except AssertionError:
        logger.debug('\t"{0}" doesn\'t exist: backup can\'t be processed!'.format(cfgfile).expandtabs(4))
        continue

    #  2.b. Get backup location.
    root = parse(cfgfile).getroot()
    directory = normpath(root.find("medium").get("path"))
    logger.debug("Backup location.")
    logger.debug('\t"%s".'.expandtabs(4) % (directory,))
    try:
        assert exists(directory) is True
    except AssertionError:
        logger.debug('\t"{0}" doesn\'t exist: backup can\'t be processed!'.format(directory).expandtabs(4))
        # continue

    #  2.c. Build backup command.
    command = ARECA + " backup"
    if arguments.full:
        command = t1.substitute(command=command, full="-f")
    if arguments.check:
        command = t2.substitute(command=command, check="-c")
    args = t3.substitute(command=command, temp=expandvars("%TEMP%"), config=cfgfile)
    args = args.split()
    logger.debug("Backup command.")
    logger.debug('\t%s.'.expandtabs(4) % (args,))

    #  2.d. Run backup command.
    code = 0
    if not arguments.test:
        process = subprocess.run(args, stdout=subprocess.PIPE, universal_newlines=True)
        code = process.returncode
        if process.returncode:
            logger.debug('"{0}" was returned by "areca_cl.exe". Backup failed.'.format(process.returncode))
            continue
        logger.info("Backup log.")
        for line in process.stdout.splitlines():
            logger.info("\t%s".expandtabs(4) % (line,))
    returncode.append(code)


# ===============
# Exit algorithm.
# ===============
if all(not operator.eq(i, 0) for i in returncode):
    sys.exit(99)
sys.exit(0)
