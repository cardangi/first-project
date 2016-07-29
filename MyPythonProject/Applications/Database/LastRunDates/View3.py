# -*- coding: ISO-8859-1 -*-
from contextlib import contextmanager
from datetime import datetime
import sqlite3
import operator
import collections
from ... import shared

__author__ = 'Xavier ROSSET'


class LastRunDates:

    keys = ["id"]
    fields = ["lastrundate"]

    def __init__(self, uid):
        self.exists = False
        self.uid = uid
        with self.toto(shared.DATABASE) as c:
            c.execute("SELECT * FROM lastrundates WHERE id=?", (self.uid,))
            r = c.fetchone()
            if r:
                self.exists = True
                self.date = r["lastrundate"]

    def readabledate(self, template):
        return shared.dateformat(shared.LOCAL.localize(self.date), template)

    def update(self, epoch):
        with self.toto(shared.DATABASE) as c:
            c.execute("UPDATE lastrundates SET lastrundate=? WHERE id=?", (datetime.fromtimestamp(epoch), self.uid,))

    def delete(self):
        with self.toto(shared.DATABASE) as c:
            c.execute("DELETE FROM lastrundates WHERE id=?", (self.uid,))

    @classmethod
    def insert(cls, **kwargs):
        v = False
        if all([operator.contains(kwargs.keys(), key) for key in cls.keys]):
            v = True
        if all([operator.contains(kwargs.keys(), key) for key in cls.fields]):
            v = True
        if v:
            with cls.toto(shared.DATABASE) as c:
                c.execute("INSERT INTO lastrundates (id, lastrundate) VALUES (?, ?)", (kwargs["id"], datetime.fromtimestamp(kwargs["lastrundate"])))
            return cls(kwargs["id"])

    @staticmethod
    @contextmanager
    def toto(database):
        conn = sqlite3.connect(database, detect_types=sqlite3.PARSE_DECLTYPES)
        conn.row_factory = sqlite3.Row
        yield conn.cursor()
        conn.commit()
        conn.close()


print("\n1 -----")
x = LastRunDates(123456797)
print(x.exists)
if x.exists:
    print(x.uid)
    print(x.date)
    print(x.readabledate(shared.TEMPLATE1))
    print(x.readabledate(shared.TEMPLATE2))
    print(x.readabledate(shared.TEMPLATE3))
    print(x.readabledate(shared.TEMPLATE4))
    print(x.readabledate(shared.TEMPLATE5))

print("\n2 -----")
y = LastRunDates(12345699)
print(y.exists)
if y.exists:
    print(y.uid)
    print(y.date)
    print(y.readabledate(shared.TEMPLATE1))
    print(y.readabledate(shared.TEMPLATE2))
    print(y.readabledate(shared.TEMPLATE3))
    print(y.readabledate(shared.TEMPLATE4))
    print(y.readabledate(shared.TEMPLATE5))

print("\n3 -----")
x.update(1469739054)
z = LastRunDates(123456797)
print(z.exists)
if z.exists:
    print(z.readabledate(shared.TEMPLATE1))
    print(z.readabledate(shared.TEMPLATE2))
    print(z.readabledate(shared.TEMPLATE3))
    print(z.readabledate(shared.TEMPLATE4))
    print(z.readabledate(shared.TEMPLATE5))

print("\n4 -----")
x = LastRunDates.insert(id=123456001, lastrundate=1469739132)
if x.exists:
    print(x.uid)
    print(x.readabledate(shared.TEMPLATE1))
    print(x.readabledate(shared.TEMPLATE2))
    print(x.readabledate(shared.TEMPLATE3))
    print(x.readabledate(shared.TEMPLATE4))
    print(x.readabledate(shared.TEMPLATE5))
