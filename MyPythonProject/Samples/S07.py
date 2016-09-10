# -*- coding: ISO-8859-1 -*-
import sqlite3
from Applications.Database.Modules import shared

__author__ = 'Xavier ROSSET'


class Encoder(object):

    def __init__(self, name, code, folder, information):
        self.name = name
        self.code = code
        self.folder = folder
        self.information = information
        self._index = 0
        self._toto = [name, code, folder, information]

    def __iter__(self):
        return self

    def __next__(self):
        if self._index == len(self._toto):
            raise StopIteration
        self._index += 1
        return self._toto[self._index - 1]


def adapt_encoder(e):
    return "{0};{1};{2};{3}".format(e.name, e.code, e.folder, e.information).encode()


def convert_encoder(e):
    w, x, y, z = [i.decode() for i in e.split(b";")]
    return Encoder(w, x, y, z)


sqlite3.register_adapter(Encoder, adapt_encoder)
sqlite3.register_converter("encoder", convert_encoder)


with shared.connectto(r"g:\computing\testdb.db") as c:

    c.execute("CREATE TABLE IF NOT EXISTS encoders (encoder ENCODER NOT NULL)")
    for row in c.execute("SELECT encoder FROM encoders ORDER BY encoder"):
        for i in row["encoder"]:
            print(i)
    c.execute("INSERT INTO encoders (encoder) VALUES (?)", (Encoder("FLAC", "13", "1.Lossless Audio Codec", "some informations"),))
    # c.execute("DROP TABLE IF EXISTS encoders")
