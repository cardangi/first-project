# -*- coding: ISO-8859-1 -*-
import os
import shutil

__author__ = 'Xavier ROSSET'


def toto(path, content):
    l = list()
    for item in content:
        if os.path.isfile(os.path.join(path, item)):
            if os.path.splitext(item)[1][1:].lower() == "jpg":
                if item[:8] != "20160229":
                    l.append(item)
            elif os.path.splitext(item)[1][1:].lower() != "jpg":
                l.append(item)
    return l


def titi(path, content):
    l = list()
    for item in content:
        if os.path.isdir(os.path.join(path, item)):
            if item != "2014":
                l.append(item)
        if os.path.isfile(os.path.join(path, item)):
            if os.path.splitext(item)[1][1:].lower() == "xmp":
                l.append(item)
    return l


class Toto(object):

    def __init__(self, **kwargs):
        self.fld = kwargs.get("fld", [])
        self.ext = kwargs.get("ext", [])
        self.fil = kwargs.get("fil", [])

    def __call__(self, path, content):
        l = list()
        for item in content:
            if os.path.isdir(os.path.join(path, item)):
                if item not in self.fld:
                    l.append(item)
            if os.path.isfile(os.path.join(path, item)):
                if os.path.splitext(item)[1][1:].lower() not in self.ext:
                    l.append(item)
        return l


if __name__ == "__main__":

    # shutil.copytree(src=r"G:\Videos\Samsung S5", dst=r"G:\Videos\Samsung S5 Copy", ignore=toto)
    shutil.copytree(src=r"G:\Pictures\Panasonic RAW", dst=r"G:\Pictures\Panasonic RAW Copy", ignore=Toto(fld=["2013", "2014"], ext=["raw"]))
