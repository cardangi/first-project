# -*- coding: utf-8 -*-
import os
import yaml
import ftplib
import logging
from base64 import b85decode
from logging.config import dictConfig
from Applications.shared import PASSWORD
from contextlib import ExitStack, ContextDecorator

__author__ = 'Xavier ROSSET'


# ========
# Classes.
# ========
class ChangeCurrentDirectory(ContextDecorator):

    def __init__(self, ftpobj, dir):
        self.dir = dir
        self.ftpobj = ftpobj
        self.cwd = ftpobj.pwd()

    def __enter__(self):
        self.ftpobj.cwd(self.dir)
        return self

    def __exit__(self, *exc):
        self.ftpobj.cwd(self.cwd)


# ==========
# Functions.
# ==========
def foldercontent(dir, ftpobj):
    for item in ftpobj.nlst(dir):
        wdir = "{0}/{1}".format(dir, item)
        stack2 = ExitStack()
        try:
            stack2.enter_context(ChangeCurrentDirectory(ftpobj, wdir))
        except SomeError:
            yield wdir
        else:
            with stack2:
                foldercontent(wdir, ftpobj)


# ========
# Logging.
# ========
with open(os.path.join(os.path.expandvars("%_COMPUTING%"), "logging.yml"), encoding="UTF_8") as fp:
    dictConfig(yaml.load(fp))
logger = logging.getLogger("Default.{0}".format(os.path.splitext(os.path.basename(__file__))[0]))


# ===============
# Main algorithm.
# ===============
stack1 = ExitStack()
try:
    ftp = stack1.enter_context(ftplib.FTP(r"192.168.1.20", timeout=30))
except TimeoutError as err:
    logger.exception(err)
else:
    with stack1:
        ftp.login(user="admin", passwd=b85decode(PASSWORD).decode())
        logger.debug(ftp.getwelcome())
        # while True:
            # try:
                # ftp.cwd("/music/S/Springsteen, Bruce")
            # except ftplib.error_perm:
                # ftp.mkd("/music/S/Springsteen, Bruce")
                # continue
            # break
        # ftp.storbinary(r'STOR {0}'.format(os.path.basename(r"F:\S\Springsteen, Bruce\2\2016\09.14 - Foxboro,  MA\CD4\1.Free Lossless Audio Codec\2.20160914.1.13.D4.T06.flac")),
                       # open(r"F:\S\Springsteen, Bruce\2\2016\09.14 - Foxboro,  MA\CD4\1.Free Lossless Audio Codec\2.20160914.1.13.D4.T06.flac", mode="rb"))
        # ftp.nlst()
        refdirectory = "/music"
        ftp.cwd(refdirectory)
        logger.debug("Current directory before: {0}.".format(ftp.pwd()))
        for file in foldercontent(refdirectory, ftp):
            logger.debug(file)
        logger.debug("Current directory after: {0}.".format(ftp.pwd()))
