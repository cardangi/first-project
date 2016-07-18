# -*- coding: ISO-8859-1 -*-
__author__ = 'Xavier ROSSET'


# =========
# Examples.
# =========
# python zipfile.py "c:\users\xavier\documents" documents onedrive --extensions documents --encrypt |--> tous les fichiers de la catégories "documents".
# python zipfile.py "c:\users\xavier\documents" documents onedrive --exclude ext1 ext2 ext3 ext4 --encrypt |--> tous les fichiers à l'exception de ceux répondant aux extensions ext1, ext2, ext3 ou ext4.
# python zipfile.py "c:\users\xavier\documents" documents onedrive --encrypt |--> tous les fichiers.
# python zipfile.py "c:\users\xavier\documents" documents onedrive --extensions documents pictures --encrypt |--> tous les fichiers des catégories "documents" ET "pictures".
# python zipfile.py "c:\users\xavier\documents" documents onedrive --extensions pictures --exclude ico --encrypt |--> tous les fichiers de la catégorie "pictures" à l'exception de ceux répondant à l'extension "ico".
# python zipfile.py "c:\users\xavier\documents" documents onedrive --extensions documents ext1 ext2 --encrypt |--> tous les fichiers de la catégorie "documents" ET les extensions ext1 et ext2.
# python zipfile.py "c:\users\xavier\documents" documents backup --extensions documents ext1 ext2 --encrypt |--> tous les fichiers de la catégorie "documents" ET les extensions ext1 et ext2.
# python zipfile.py "c:\users\xavier\documents" documents "y:\backup" --extensions documents ext1 ext2 --encrypt |--> tous les fichiers de la catégorie "documents" ET les extensions ext1 et ext2.


# ========
# Imports.
# ========
import os
import shutil
import zipfile
import logging
import tempfile
import argparse
from .. import shared
from pytz import timezone
from datetime import datetime
from sortedcontainers import SortedList, SortedDict
from os.path import expandvars, isdir, join, normpath, relpath, splitext


# ==========
# Constants.
# ==========
DESTINATIONS = {"documents": shared.Global()["documents"],
                "onedrive": shared.Global()["onedrive"],
                "temp": expandvars("%temp%"),
                "backup": shared.Global()["backup"]}
CONSTANTS = SortedDict({k: shared.Global()[k] for k in list(shared.Global().keys())})


# ==========
# Functions.
# ==========
def validdirectory(d):
    if not os.path.isdir(d):
        raise argparse.ArgumentTypeError('"{}" is not a valid directory'.format(d))
    if not os.access(d, os.R_OK):
        raise argparse.ArgumentTypeError('"{}" is not a readable directory'.format(d))
    return d


def validdestination(d):
    if d not in DESTINATIONS:
        raise argparse.ArgumentTypeError('"{}" is not a valid destination'.format(d))
    return d


def insertextension(ext):
    """
    :param ext: liste regroupant des extensions ou des listes d'extensions.
    :return: liste regroupant l'ensemble des extensions résultantes.
    """
    extensions, l = {"documents": ("ods", "odt", "pdf", "txt", "xav"),
                     "pictures": ("jpg", "png", "ico"),
                     "audio": ("flac", "mp3", "m4a", "ogg"),
                     "video": ("mts", "m2ts", "mov", "mp4"),
                     "python": ("py", "vbs")},\
                    SortedList()
    for i in ext:
        if i in list(extensions.keys()):
            for j in extensions[i]:
                l.add(j)
        if i not in list(extensions.keys()):
            l.add(i)
    return l


def removeextension(ext, exttoremove):
    """
    :param ext: liste regroupant des extensions.
    :param exttoremove:  liste regroupant des extensions à retirer.
    :return: liste regroupant l'ensemble des extensions résultantes.
    """
    for i in exttoremove:
        if i in ext:
            ext.remove(i)
    return ext


# =================
# Arguments parser.
# =================
parser = argparse.ArgumentParser()
parser.add_argument("directory", help="browsed directory", type=validdirectory)
parser.add_argument("archive", help="archive name")
parser.add_argument("destination", help="archive destination", type=validdestination)
parser.add_argument("-e", "--extensions", help="archived extension(s)", nargs="*")
parser.add_argument("-x", "--exclude", help="excluded extension(s)", nargs="*")
parser.add_argument("-c", "--encrypt", help="encrypt file(s)", action="store_true")
parser.add_argument("-d", "--debug", action="store_true")
arguments = parser.parse_args()


# ========
# Logging.
# ========
logger = logging.getLogger("%s.%s" % (__package__, os.path.basename(__file__)))


# ==================
# Initialization(s).
# ==================
dst, archive, count, l1, exttoremove, exttoinsert, first = None, None, 0, SortedList(), [], [], True


# ===============
# Main algorithm.
# ===============

# Start logging.
logger.info("{0} {1} {0}".format("="*50, datetime.now(tz=timezone(CONSTANTS["defaulttimezone"])).strftime(CONSTANTS["defaultdatepattern"])))
logger.info('START "%s".' % (os.path.basename(__file__),))
logger.info("------------")
logger.info("Argument(s).")
logger.info("------------")
logger.info('\t- %s "%s".'.expandtabs(4) % ("directory\t:".expandtabs(12), arguments.directory))
logger.info('\t- %s "%s".'.expandtabs(4) % ("destination\t:".expandtabs(12), arguments.destination))
debug, encrypt = "N", "N"
if arguments.encrypt:
    encrypt = "Y"
if arguments.debug:
    debug = "Y"
logger.info("\t- %s %s.".expandtabs(4) % ("debug\t:".expandtabs(12), debug))
logger.info("\t- %s %s.".expandtabs(4) % ("encrypt\t:".expandtabs(12), encrypt))

# Construction de la liste des extensions à archiver.
if arguments.extensions:
    exttoinsert = arguments.extensions
if arguments.exclude:
    exttoremove = arguments.exclude
l2 = removeextension(ext=insertextension(ext=exttoinsert), exttoremove=exttoremove)

# Restitution des extensions sélectionnées.
logger.info("-------------")
logger.info("Extension(s).")
logger.info("-------------")
for ext in l2:
    logger.info("\t%s.".expandtabs(4) % ext)

# Navigation récursive du répertoire reçu en paramètre pour sélection des fichiers répondant aux extensions à archiver.
for f in shared.directorytree(arguments.directory):
    file = shared.File(f)
    addfile = False
    if (l2 and file["extension"].lower() in l2) or not l2:
        addfile = True
    if addfile:
        l1.add(f)

# Traitement individuel de chaque fichier retenu pour l'archivage.
if l1:

    # os.pardir = ".."
    # refpath = "C:\Users\Xavier\AppData\Local\Temp\1282856126" si arguments.directory = "C:\Users\Xavier\AppData\Local\Temp\1282856126\documents".
    # refdir = "documents".

    refpath = normpath(join(arguments.directory, os.pardir))
    refdir = relpath(arguments.directory, refpath)

    with tempfile.TemporaryDirectory() as tmpdir:

        # Constitution de l'archive.
        archive = r"{0}\{1}.zip".format(tmpdir, arguments.archive)
        # -----
        logger.info("--------")
        logger.info("Archive.")
        logger.info("--------")
        logger.info('\t"%s".'.expandtabs(4) % archive)
        # -----
        with zipfile.ZipFile(archive, shared.Global()["write"]) as zipfil:
            zipfil.write(arguments.directory, arcname=refdir)
            # -----
            logger.info("--------")
            logger.info("File(s).")
            logger.info("--------")
            # -----
            for item in l1:
                count += 1
                # -----
                if not first:
                    logger.info("")
                logger.info('\t%03d. "%s".'.expandtabs(4) % (count, item))
                logger.info("\t---".expandtabs(4))
                # -----
                filetozip = shared.File(item)
                if filetozip.exists:
                    dirname = relpath(filetozip["dirname"], refpath)
                    if not os.path.exists(join(tmpdir, dirname)):
                        os.makedirs(join(tmpdir, dirname))
                    # -----
                    logger.debug("\tAttribute(s).".expandtabs(4))
                    for k, v in filetozip:
                        logger.debug('\t- "%s": "%s".'.expandtabs(8) % (k, v))
                    # -----
                    rtnval = 0
                    if arguments.encrypt:
                        logger.info("\tEncrypt file.".expandtabs(4))
                        rtnval = filetozip.encrypt(dst=join(tmpdir, dirname), rcp=CONSTANTS["recipient"])
                        if rtnval == 0:
                            filetozip = shared.File(splitext(filetozip.renameto(basn="{0}.{1}.gpg".format(filetozip["basename"], filetozip["extension"]), dirn=join(tmpdir, dirname)))[0])
                            # -----
                            if filetozip.exists:
                                logger.info("\tEncryption succeeded.".expandtabs(4))
                                logger.debug('\t"%s" created.'.expandtabs(4) % filetozip["name"])
                            else:
                                logger.info("\tEncryption failed.".expandtabs(4))
                            # -----
                    if rtnval == 0 and filetozip.exists:
                            arcname = relpath(filetozip["name"], refpath)
                            if arguments.encrypt:
                                arcname = "%s.%s" % (join(dirname, filetozip["basename"]), filetozip["extension"])
                            zipfil.write(filetozip["name"], arcname=arcname)
                            # -----
                            logger.info('\t"%s" appended to archive.'.expandtabs(4) % filetozip["name"])
                            logger.debug('\tArchive relative path is: "%s".'.expandtabs(4) % arcname)
                            # arcname = "documents\C\Users\Xavier\Documents\99 - bootlegs.txt.gpg" si
                            #  filetozip["name"] = "C:\Users\Xavier\AppData\Local\Temp\1282856126\documents\C\Users\Xavier\Documents\99 - bootlegs.txt.gpg"

                    first = False

        # Copie de l'archive vers l'emplacement de destination.
        dst = DESTINATIONS.get(arguments.destination, "")
        if not dst:
            dst = arguments.destination
        if isdir(dst):
            shutil.copy(src=archive, dst=dst)
            logger.info("")
            logger.info("Copy archive to destination.")
            logger.info('\tSrc ("%s").'.expandtabs(4) % archive)
            logger.info('\tDst ("%s").'.expandtabs(4) % dst)

# End logging.
logger.info('END "%s".' % (os.path.basename(__file__),))
