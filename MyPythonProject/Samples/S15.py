# -*- coding: utf-8 -*-
import os
import json
import yaml
import ftplib
import logging
from base64 import b85decode
from contextlib import ExitStack
from logging.config import dictConfig
from Applications.shared import NAS, PASSWORD, ChangeRemoteCurrentDirectory

__author__ = 'Xavier ROSSET'


# ===============
# Main algorithm.
# ===============
if __name__ == "__main__":

    # --> Logging.
    with open(os.path.join(os.path.expandvars("%_COMPUTING%"), "logging.yml"), encoding="UTF_8") as fp:
        dictConfig(yaml.load(fp))
    logger = logging.getLogger("Default.{0}".format(os.path.splitext(os.path.basename(__file__))[0]))

    # JSON avec ["S\Springsteen, Bruce\2\2016\09.14 - Foxboro,  MA\CD4\1.Free Lossless Audio Codec\2.20160914.1.13.D4.T01.flac", "S\Springsteen, Bruce\2\2016\09.14 - Foxboro,  MA\CD4\1.Free Lossless Audio Codec\2.20160914.1.13.D4.T02.flac"]
    # On extrait les deux premiers répertoires et le tag "albumsort" pour créer une variable "S\Springsteen, Bruce\2.20160914.1".
    with open(myfile) as fp:

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
                ftp.cwd(refdirectory)
                for item in json.load(fp):
                    wdir = "{0}/{1}".format(refdirectory, output.replace("\\", "/"))  # "S/Springsteen, Bruce/2.20160914.1".
                    stack2 = ExitStack()
                    while True:
                        try:
                            stack2.enter_context(ChangeRemoteCurrentDirectory(ftp, wdir))
                        except ftplib.error_perm:
                            logger.debug('"{0}" created.'.format(wdir))
                            ftp.mkd(wdir)
                            continue
                        else:
                            with stack2:
                                ftp.storbinary(r"STOR {0}".format(os.path.basename(item)), open(item, mode="rb"))
                            break
