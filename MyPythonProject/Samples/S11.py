# -*- coding: utf-8 -*-
import os
import yaml
import ftplib
import logging
from base64 import b85decode
from contextlib import ExitStack
from logging.config import dictConfig
from Applications.shared import NAS, PASSWORD, ChgCurDir

__author__ = 'Xavier ROSSET'


# ==========
# Functions.
# ==========
def directorycontent(*extensions, ftpobject, currentdir, logobject=None, excluded=None):
    regex = None
    if excluded:
        rex = r"{0}/(?:{1})".format(currentdir, "|".join(excluded))
        regex = re.compile(rex, re.IGNORECASE)
    for item in ftpobject.nlst():
        wdir = "{0}/{1}".format(currentdir, item)
        if logobject:
            logobject.debug(currentdir)
            logobject.debug(item)
            logobject.debug(wdir)
        if regex and regex.match(wdir):
            continue
        stack2 = ExitStack()
        try:
            stack2.enter_context(ChgCurDir(ftpobject, wdir))
        except ftplib.error_perm:
            if not extensions or (extensions and os.path.splitext(wdir)[1].lower in (extension.lower() for extension in extensions)):
                yield wdir
        else:
            with stack2:
                for content in directorycontent(*extensions, ftpobject=ftpobject, currentdir=wdir, logobject=logobject, excluded=excluded):
                    yield content


# ===============
# Main algorithm.
# ===============
if __name__ == "__main__":

    # --> Logging.
    with open(os.path.join(os.path.expandvars("%_COMPUTING%"), "logging.yml"), encoding="UTF_8") as fp:
        dictConfig(yaml.load(fp))
    logger = logging.getLogger("Default.{0}".format(os.path.splitext(os.path.basename(__file__))[0]))

    # --> Main alogrithm.
    stack1 = ExitStack()
    try:
        ftp = stack1.enter_context(ftplib.FTP(NAS, timeout=30))
    except TimeoutError as err:
        logger.exception(err)
    else:
        with stack1:
            ftp.login(user="admin", passwd=b85decode(PASSWORD).decode())
            logger.debug(ftp.getwelcome())
            refdirectory = "/music"
            try:
                ftp.cwd(refdirectory)
            except ftplib.error_perm as err:
                logger.exception(err)
            else:
                logger.debug("Current directory before: {0}.".format(ftp.pwd()))
                for file in directorycontent("ape", "mp3", "m4a", "flac", "ogg", ftpobject=ftp, currentdir=refdirectory):
                    logger.debug(file)
                logger.debug("Current directory after: {0}.".format(ftp.pwd()))
