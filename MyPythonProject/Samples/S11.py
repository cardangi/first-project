# -*- coding: utf-8 -*-
import os
import yaml
import ftplib
import logging
from base64 import b85decode
from logging.config import dictConfig
from Applications.shared import PASSWORD
from contextlib import ExitStack

__author__ = 'Xavier ROSSET'


# ========
# Classes.
# ========
class Toto(object):

    def __init__(self, ftpobj, dir):
        self.dir = dir
        self.ftpobj = ftpobj
        self.cwd = ftpobj.pwd()

    def __enter__(self):
        self.ftpobj.cwd(self.dir)
        return self

    def __exit__(self, *exc):
        self.ftpobj.cwd(self.cwd)


# ========
# Logging.
# ========
with open(os.path.join(os.path.expandvars("%_COMPUTING%"), "logging.yml"), encoding="UTF_8") as fp:
    dictConfig(yaml.load(fp))
logger = logging.getLogger("Default.{0}".format(os.path.splitext(os.path.basename(__file__))[0]))


# ===============
# Main algorithm.
# ===============
stack = ExitStack()
try:
    ftp = stack.enter_context(ftplib.FTP(r"192.168.1.20", timeout=30))
except TimeoutError as err:
    logger.debug(err)
else:
    with stack:
        ftp.login(user="admin", passwd=b85decode(PASSWORD).decode())
        logger.debug(ftp.getwelcome())
        while True:
            try:
                ftp.cwd("/music/S/Springsteen, Bruce")
            except ftplib.error_perm:
                ftp.mkd("/music/S/Springsteen, Bruce")
                continue
            break
        ftp.storbinary(r'STOR {0}'.format(os.path.basename(r"F:\S\Springsteen, Bruce\2\2016\09.14 - Foxboro,  MA\CD4\1.Free Lossless Audio Codec\2.20160914.1.13.D4.T06.flac")),
                       open(r"F:\S\Springsteen, Bruce\2\2016\09.14 - Foxboro,  MA\CD4\1.Free Lossless Audio Codec\2.20160914.1.13.D4.T06.flac", mode="rb"))
        ftp.nlst()
        ftp.cwd("/music")
        for file in ftp.nlst():
            logger.debug(file)
            with Toto(ftp, r"/music/{0}".format(file)):
                for subfile in ftp.nlst():
                    logger.debug(subfile)
                    with Toto(ftp, r"/music/{0}/{1}".format(file, subfile)):
                        for subsubfile in ftp.nlst():
                            logger.debug(subsubfile)
