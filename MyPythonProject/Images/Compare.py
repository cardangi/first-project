# -*- coding: utf-8 -*-
import os
import yaml
import ftplib
import logging
from base64 import b85decode
from contextlib import ExitStack
from logging.config import dictConfig
from Images.LocalCollection import images
from Applications.shared import NAS, PASSWORD
from Images.RemoteCollection import remotedirectorycontent

__author__ = 'Xavier ROSSET'


# ===============
# Main algorithm.
# ===============
if __name__ == "__main__":

    remote, local = [], None

    # --> Logging.
    with open(os.path.join(os.path.expandvars("%_COMPUTING%"), "logging.yml"), encoding="UTF_8") as fp:
        dictConfig(yaml.load(fp))
    logger = logging.getLogger("Images.{0}".format(os.path.splitext(os.path.basename(__file__))[0]))

    # --> Main algorithm.
    stack1 = ExitStack()
    try:
        ftp = stack1.enter_context(ftplib.FTP(NAS, timeout=30))
    except TimeoutError as err:
        logger.exception(err)
    else:
        with stack1:
            ftp.login(user="admin", passwd=b85decode(PASSWORD).decode())
            logger.debug(ftp.getwelcome())
            refdirectory = "/pictures"
            try:
                ftp.cwd(refdirectory)
            except ftplib.error_perm as err:
                logger.exception(err)
            else:
                remote.extend([os.path.basename(image) for image in remotedirectorycontent("jpg", ftpobject=ftp, currentdir=refdirectory, excluded=["#recycle"])])

                # --> Remote collection.
                remote = set(remote)

                # --> Local collection.
                local = set(map(os.path.basename, images()))

                difference = sorted(local - remote)
                # for image in difference:
                #     logger.debug(image)
                logger.debug("Differences: {0}".format(len(difference)))

                common = sorted(local & remote)
                # for image in common:
                #     logger.debug(image)
                logger.debug("Common: {0}".format(len(common)))
