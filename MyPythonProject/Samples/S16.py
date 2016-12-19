# -*- coding: utf-8 -*-
import os
import yaml
import ftplib
import logging
from base64 import b85decode
from contextlib import ExitStack
from logging.config import dictConfig
from Applications.shared import NAS, PASSWORD, IMAGES, ChangeRemoteCurrentDirectory, filesinfolder

__author__ = 'Xavier ROSSET'


# ==========
# Functions.
# ==========
def directorycontent(ftpobject, currentdir, logobject=None):
    for item in ftpobject.nlst():
        wdir = "{0}/{1}".format(currentdir, item)
        if logobject:
            logobject.debug(currentdir)
            logobject.debug(item)
            logobject.debug(wdir)
        stack2 = ExitStack()
        try:
            stack2.enter_context(ChangeRemoteCurrentDirectory(ftpobject, wdir))
        except ftplib.error_perm:
            yield wdir
        else:
            with stack2:
                for content in directorycontent(ftpobject=ftpobject, currentdir=wdir, logobject=logobject):
                    yield content


# ===============
# Main algorithm.
# ===============
if __name__ == "__main__":

    x, y = [], []

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
            for directory in ["/pictures"]:
                if directory.lower() == "recycle":
                    continue
                ftp.cwd(directory)
                x.extend([os.path.basename(file) for file in directorycontent(ftpobject=ftp, currentdir=directory) if os.path.splitext(file)[1][1:].lower() == "jpg"])

        x = set(x)
        # logger.debug(x)
        y = set(map(os.path.basename, filesinfolder("jpg", folder=IMAGES, excluded=["Recover", "iPhone", "Recycle", "\$Recycle"])))
        # logger.debug(y)
        z = sorted(x & y)
        logger.debug(z)
        logger.debug(len(z))
        w = sorted(y - x)
        logger.debug(w)
        logger.debug(len(w))
