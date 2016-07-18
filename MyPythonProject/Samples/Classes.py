# -*- coding: ISO-8859-1 -*-


# ===================
# Absolute import(s).
# ===================
# from contextlib import contextmanager
# from collections import OrderedDict
# from datetime import datetime
# import os.path
# import logging
# import sqlite3


# =========
# Comments.
# =========
# __author__ = 'Xavier ROSSET'


# ========
# Classes.
# ========
# class Global:
#     """
#     Utilisation de la classe "Global" :
#     print(rec)
#     rec = shared.Global()
#     print(rec["database"])
#     print(rec.database)
#     print(list(rec.keys()))
#     """
    # consts = {"database": r"g:\computing\database.db"}
    #
    # def __getitem__(self, itm):
    #     return self.consts[itm]
    #
    # def __init__(self):
    #     for k in list(self.consts.keys()):
    #         setattr(self, k, self.consts[k])
    #
    # def __repr__(self):
    #     return repr(self.consts)
    #
    # def keys(self):
    #     return self.consts.__iter__()


# class Table:
#     """
#     Utilisation de la classe "Table" :
#     table = Table(table="rippinglog")
#     if table.exists:
#         print(len(table))
#         for pkey in table:
#             print(pkey)
#         print(table[0])
#         print(table[len(table)-1])
#     Pour rendre toute instance de "Table" itérable, déclarer soit la méthode __iter__().
#     Voir "http://nedbatchelder.com/text/iter.html"
#     """
#
#     def __getitem__(self, itm):
#         return self.pkey[itm]
#
#     def __init__(self, table, database=Global()["database"]):
#         self.database = database
#         self.table = table
#         self.fld = ()
#         self.key = ()
#         self.pkey = []
#         self.exists = False
#         self.index = 0
#         select = ""
#         # -----
#         conn = sqlite3.connect(database)
#         cursor = conn.cursor()
#         cursor.execute("PRAGMA table_info({0})".format(table))
#         a = cursor.fetchall()
#         conn.close()
#         # -----
#         self.fld = tuple([i[1] for i in a])
#         self.key = tuple([i[1] for i in a if i[5] > 0])
#         # -----
#         if self.fld:
#             self.exists = True
#             if self.key:
#                 for key in self.key:
#                     select = "{0}{1}, ".format(select, key)
#                 self.pkey = runqrystatement(db=database, qry="SELECT {0} FROM {1} ORDER BY {0}".format(select[:-2], table))
#
#     def __iter__(self):
#         for pkey in self.pkey:
#             yield pkey
#
#     def __len__(self):
#         return len(self.pkey)


# class Record:
#     """
#     Utilisation de la classe "Record" :
#     -----
#     rec = Record(1234567, table=Table(table="rippinglog"))
#     if rec.exists:
#         print(rec)
#         if "artist" in rec:
#             print(rec["artist"])
#         for key in list(rec.keys()):
#             print("{0} : {1}".format(key, rec[key]))
#     -----
#         rec.update(genre="Hard Rock")
#         for key in list(rec.keys()):
#             print("{0} : {1}".format(key, rec[key]))
#     -----
#         rec.delete()
#         print(rec.exists)
#     -----
#     rec = Record.insert(table=Table(table="flags"), id=1234567, flag=0)
#     if rec.exists:
#         print(rec["flag"])
#         for key in list(rec.keys()):
#             print("{0} : {1}".format(key, rec[key]))
#     """
#
#     def __contains__(self, itm):
#         return itm in self.data
#
#     def __getitem__(self, itm):
#         return self.data[itm]
#
#     def __init__(self, *pkey, table):
#         self.data = {}
#         self.table = table
#         self.pkey = pkey
#         self.exists = False
#         data, select, where = [], "", ""
#         # -----
#         if table.exists:
#             for fld in table.fld:
#                 select = "{0}{1}, ".format(select, fld)
#             for key in table.key:
#                 where = "{0}{1}=? and ".format(where, key)
#             data = runqrystatement(*pkey, qry="SELECT {0} FROM {1} WHERE {2}".format(select[:-2], table.table, where[:-5]))
#             if data:
#                 self.exists = True
#                 self.data = OrderedDict(zip(table.fld, data[0]))
#
#     def __repr__(self):
#         return repr(self.data)
#
#     @classmethod
#     def insert(cls, table, **kwargs):
#         # -----
#         fields, placeholders, values, psargs = "", "", (), ()
#         # -----
#         for key in list(kwargs.keys()):
#             if key in table.fld:
#                 fields = "{0}{1}, ".format(fields, key)
#                 placeholders = "{0}?, ".format(placeholders)
#                 values += (kwargs[key],)
#             if key in table.key:
#                 psargs += (kwargs[key],)
#         # -----
#         for key in table.key:
#             if key not in list(kwargs.keys()):
#                 fields = "{0}{1}, ".format(fields, key)
#                 placeholders = "{0}?, ".format(placeholders)
#                 values += (None,)
#         # -----
#         runqrystatement(*values, qry="INSERT INTO {0} ({1}) VALUES ({2})".format(table.table, fields[:-2], placeholders[:-2]))
#         # -----
#         if not psargs:
#             fields, order = "", ""
#             for key in table.key:
#                 fields = "%s%s, " % (fields, key)
#                 order = "%s%s DESC, " % (order, key)
#             psargs = runqrystatement(qry="SELECT %s FROM %s ORDER BY %s" % (fields[:-2], table.table, order[:-2]))[0]
#         # -----
#         return cls(*psargs, table=Table(table=table.table))
#
#     def update(self, **kwargs):
#         set, where, psargs = "", "", ()
#         for key in list(kwargs.keys()):
#             if key in self.table.fld:
#                 if key not in self.table.key:
#                     set = "{0}{1}=?, ".format(set, key)
#                     psargs += (kwargs[key],)
#         for key in self.table.key:
#             where = "{0}{1}=? and ".format(where, key)
#         for pkey in self.pkey:
#             psargs += (pkey,)
#         runqrystatement(*psargs, qry="UPDATE {0} SET {1} WHERE {2}".format(self.table.table, set[:-2], where[:-5]))
#         self.__init__(*self.pkey, table=self.table)
#
#     def delete(self):
#         where, psargs = "", ()
#         for key in self.table.key:
#             where = "{0}{1}=? and ".format(where, key)
#         for pkey in self.pkey:
#             psargs += (pkey,)
#         runqrystatement(*psargs, qry="DELETE FROM {0} WHERE {1}".format(self.table.table, where[:-5]))
#         self.__init__(*self.pkey, table=self.table)
#
#     def keys(self):
#         return self.data.keys()
#
#
# class RippingLog(Record):
#
#     def __init__(self, *pkey):
#         super(RippingLog, self).__init__(*pkey, table=Table("rippinglog"))
#
#     @classmethod
#     def duplicate(cls, *pkey, **kwargs):
#         # -----
#         fields, placeholders, values = "", "", ()
#         # -----
#         table = Table("rippinglog")
#         rec = Record(*pkey, table=table)
#         # -----
#         rec.data["id"] = None
#         rec.data["ripped"] = datetime.now()
#         # -----
#         for arg in list(kwargs.keys()):
#             if arg in table.fld and arg not in table.key:
#                 rec.data[arg] = kwargs[arg]
#         # -----
#         for key in list(rec.data.keys()):
#             fields = "{0}{1}, ".format(fields, key)
#             placeholders = "{0}?, ".format(placeholders)
#             values += (rec.data[key],)
#         # -----
#         conn = sqlite3.connect(table.database)
#         conn.cursor().execute("INSERT INTO {0} ({1}) VALUES ({2})".format(table.table, fields[:-2], placeholders[:-2]), values)
#         conn.commit()
#         # -----
#         fields, order = "", ""
#         for key in table.key:
#             fields = "%s%s, " % (fields, key)
#             order = "%s%s DESC, " % (order, key)
#         psargs = conn.cursor().execute("SELECT %s FROM %s ORDER BY %s" % (fields[:-2], table.table, order[:-2])).fetchone()
#         conn.close()
#         # -----
#         return cls(*psargs)


# ==========
# Functions.
# ==========
# def runqrystatement(*psargs, db=Global()["database"], **kwargs):
#
#     # os.path.basename(__file__) : "shared.py".
#     # os.path.splitext(os.path.basename(__file__))[0].capitalize() : "Shared".
#     # Le logger "Applications.CDRipper" a été créé dans "Applications.CDRipper.__init__.py" pour les scripts exécutés depuis cette application.
#     # Il ne faut donc surtout pas configuer une deuxième fois un logger "Applications.CDRipper" au risque de doublonner le fichier log résultant.
#     # En revanche le logger ne fonctionnera pas pour les scripts exécutés depuis une autre application.
#     # logger = logging.getLogger("Applications.CDRipper.Runqrystatement")
#
#     @contextmanager
#     def dbconnect(database):
#         conn = sqlite3.connect(database, detect_types=sqlite3.PARSE_DECLTYPES)
#         yield conn.cursor()
#         conn.commit()
#         conn.close()
#
#     qry = kwargs.get("qry", "")
#     if qry:
#         with dbconnect(database=db) as csr:
#             csr.execute(qry, psargs)
#             if qry.lower().startswith("select"):
#                 return csr.fetchall()
