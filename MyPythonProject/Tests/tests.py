# -*- coding: utf-8 -*-
import os
import json
import yaml
import logging
import sqlite3
import unittest
import tempfile
from shutil import copy
from operator import eq, lt, gt
from Applications import shared
from logging.config import dictConfig
from collections import MutableSequence
from Applications.Database.DigitalAudioFiles.shared import parser, updatealbum
from Applications.AudioCD.shared import DefaultCDTrack, RippedCD, canfilebeprocessed, digitalaudiobase, rippinglog

__author__ = 'Xavier ROSSET'


# ========
# Logging.
# ========
with open(os.path.join(os.path.expandvars("%_COMPUTING%"), "logging.yml"), encoding=shared.UTF8) as fp:
    dictConfig(yaml.load(fp))
logger = logging.getLogger(os.path.splitext(os.path.basename(__file__))[0])


# ========
# Classes.
# ========
class Test01(unittest.TestCase):

    def setUp(self):
        self.ref = [1, 2, 3, 4, 5, 6, 7, 8]

    def test_01first(self):
        self.assertTrue(all([lt(x, 50) for x in self.ref]))

    def test_02second(self):
        self.assertFalse(all([gt(x, 50) for x in self.ref]))

    def test_03third(self):
        self.assertTrue(any([gt(x, 5) for x in self.ref]))

    def test_04fourth(self):
        self.assertTrue(any([eq(x, 5) for x in self.ref]))

    def test_05fifth(self):
        self.assertFalse(all([eq(x, 5) for x in self.ref]))


class Test02(unittest.TestCase):

    def setUp(self):

        class MyClass(MutableSequence):

            def __init__(self, seq):
                self._index = 0
                self._seq = sorted(sorted(sorted(seq, key=self.f1), key=self.f2), key=self.f3)

            def __getitem__(self, item):
                return self._seq[item]

            def __setitem__(self, key, value):
                self._seq[key] = value

            def __delitem__(self, key):
                del self._seq[key]

            def __len__(self):
                return len(self._seq)

            def __iter__(self):
                for item in self._seq:
                    yield item[2:6]

            def __call__(self):
                self._index += 1
                return self._seq[self._index - 1][2:6]

            @property
            def indexes(self):
                return self._seq

            def insert(self, index, value):
                self._seq.insert(index, value)

            @staticmethod
            def f1(s):
                return int(s.split(".")[0])

            @staticmethod
            def f2(s):
                return int(s.split(".")[2])

            @staticmethod
            def f3(s):
                return int(s.split(".")[1])

        self.x = MyClass(["2.20160125.13", "2.20160201.13", "2.20160120.13", "1.20160625.13", "2.20160422.13", "1.20160422.13", "2.20160422.15", "2.19841102.13", "2.19990822.13", "2.20021014.13", "2.20000823.13", "2.20170101.13"])

    def test_01first(self):
        self.assertListEqual(self.x.indexes, ["2.19841102.13", "2.19990822.13", "2.20000823.13", "2.20021014.13", "2.20160120.13", "2.20160125.13", "2.20160201.13", "1.20160422.13", "2.20160422.13", "2.20160422.15", "1.20160625.13", "2.20170101.13"])

    def test_02second(self):
        self.assertListEqual(list(self.x), ["1984", "1999", "2000", "2002", "2016", "2016", "2016", "2016", "2016", "2016", "2016", "2017"])

    def test_03third(self):
        self.assertListEqual(list(iter(self.x, "2016")), ["1984", "1999", "2000", "2002"])


class TestRegex(unittest.TestCase):
    """
    Test regular expressions.
    """

    def test_01first(self):
        self.assertRegex("1.19840000.1.13", r"^(?=1\.\d[\d.]+$)(?=[\d.]+\.13$)1\.(?:{0})0000\.\d\.13$".format(shared.DFTYEARREGEX))

    def test_02second(self):
        self.assertNotRegex("1.19840000.1.15", r"^(?=1\.\d[\d.]+$)(?=[\d.]+\.13$)1\.(?:{0})0000\.\d\.13$".format(shared.DFTYEARREGEX))

    def test_03third(self):
        self.assertNotRegex("1.19840000.1", r"^(?=1\.\d[\d.]+$)(?=[\d.]+\.13$)1\.(?:{0})0000\.\d\.13$".format(shared.DFTYEARREGEX))

    def test_04fourth(self):
        self.assertNotRegex("2.20160529.1.13", r"^(?=1\.\d[\d.]+$)(?=[\d.]+\.13$)1\.(?:{0})0000\.\d\.13$".format(shared.DFTYEARREGEX))

    def test_05fifth(self):
        self.assertNotRegex("2.99999999.1.13", r"^(?=1\.\d[\d.]+$)(?=[\d.]+\.13$)1\.(?:{0})0000\.\d\.13$".format(shared.DFTYEARREGEX))

    def test_06sixth(self):
        self.assertRegex("1994.1 - Dissident", r"^(?:{0})\.\d -\B".format(shared.DFTYEARREGEX))

    def test_07seventh(self):
        self.assertNotRegex("Dissident", r"^(?:{0})\.\d -\B".format(shared.DFTYEARREGEX))

    def test_08eighth(self):
        self.assertNotRegex("1994 - Dissident", r"^(?:{0})\.\d -\B".format(shared.DFTYEARREGEX))


class TestEnumerateTuplesList(unittest.TestCase):

    def test_01first(self):
        self.assertListEqual([(1, "path1", "file1"), (2, "path2", "file2"), (3, "path3", "file3"), (4, "path4", "file4"), (5, "path6", "file6")], shared.enumeratetupleslist([("path1", "file1"),
                                                                                                                                                                              ("path2", "file2"),
                                                                                                                                                                              ("path3", "file3"),
                                                                                                                                                                              ("path6", "file6"),
                                                                                                                                                                              ("path4", "file4")
                                                                                                                                                                              ])
                             )


class TestEnumerateSortedListContent(unittest.TestCase):

    def test_01first(self):
        self.assertListEqual([(1, "path1"), (2, "path2"), (3, "path3"), (4, "path4"), (5, "path6")], shared.enumeratesortedlistcontent(["path1", "path2", "path3", "path6", "path4"]))


class TestCanFileBeProcessed(unittest.TestCase):

    def test_01first(self):
        self.assertTrue(canfilebeprocessed("flac", *()))

    def test_02second(self):
        self.assertFalse(canfilebeprocessed("pdf", *()))

    def test_03third(self):
        self.assertTrue(canfilebeprocessed("flac", *("flac",)))

    def test_04fourth(self):
        self.assertFalse(canfilebeprocessed("mp3", *("flac",)))

    def test_05fifth(self):
        self.assertFalse(canfilebeprocessed("flac", *("pdf",)))

    def test_06sixth(self):
        self.assertTrue(canfilebeprocessed("FLAC", *()))

    def test_07seventh(self):
        self.assertFalse(canfilebeprocessed("PDF", *()))

    def test_08eighth(self):
        self.assertTrue(canfilebeprocessed("FLAC", *("flac",)))

    def test_09ninth(self):
        self.assertTrue(canfilebeprocessed("flac", *("FLAC",)))

    def test_10tenth(self):
        self.assertTrue(canfilebeprocessed("FLAC", *("FLAC",)))


class Test01DefaultCDTrack(unittest.TestCase):
    """
    Test "Applications.AudioCD.shared.DefaultCDTrack".
    """
    def setUp(self):

        # Default single CD tags.
        # Both artist and artistsort are identical.
        # "origyear" is not provided.
        tags1 = {
            "Album": "Abigail",
            "Year": "1987",
            "Disc": "1/1",
            "Label": "Roadrunner Records",
            "UPC": "016861878825",
            "Artist": "King Diamond",
            "AlbumSortCount": "1",
            "Live": "N",
            "_albumart_1_Front Album Cover": r"C:\Users\Xavier\AppData\Local\Temp\dbp49F2.tmp\9.bin",
            "Track": "9/13",
            "Profile": "Default",
            "Rating": "8",
            "Source": "CD (Lossless)",
            "Encoder": "(FLAC 1.3.0)",
            "ArtistSort": "King Diamond",
            "AlbumArtistSort": "King Diamond",
            "AlbumArtist": "King Diamond",
            "Genre": "Rock",
            "InCollection": "Y",
            "TitleLanguage": "English",
            "Bootleg": "N",
            "Title": "A Mansion in Darkness"
        }

        # Default single CD tags.
        # Both "artist" and "artistsort" are identical.
        # "origyear" is provided.
        tags2 = {
            "Album": "Abigail",
            "Year": "2016",
            "Disc": "1/1",
            "Label": "Roadrunner Records",
            "UPC": "016861878825",
            "Artist": "King Diamond",
            "AlbumSortCount": "1",
            "Live": "N",
            "_albumart_1_Front Album Cover": r"C:\Users\Xavier\AppData\Local\Temp\dbp49F2.tmp\9.bin",
            "Track": "9/13",
            "Profile": "Default",
            "Rating": "8",
            "Source": "CD (Lossless)",
            "Encoder": "(FLAC 1.3.0)",
            "ArtistSort": "King Diamond",
            "AlbumArtistSort": "King Diamond",
            "AlbumArtist": "King Diamond",
            "Genre": "Rock",
            "InCollection": "Y",
            "TitleLanguage": "English",
            "Bootleg": "N",
            "Title": "A Mansion in Darkness",
            "OrigYear": "1987"
        }
        self.track1 = DefaultCDTrack(**{k.lower(): v for k, v in tags1.items()})
        self.track2 = DefaultCDTrack(**{k.lower(): v for k, v in tags2.items()})

    def test_01first(self):
        self.assertEqual(self.track1.discnumber, "1")

    def test_02second(self):
        self.assertEqual(self.track1.totaldiscs, "1")

    def test_03third(self):
        self.assertEqual(self.track1.tracknumber, "9")

    def test_04fourth(self):
        self.assertEqual(self.track1.totaltracks, "13")

    def test_05fifth(self):
        self.assertEqual(self.track1.albumsort, "1.19870000.1.13")

    def test_06sixth(self):
        self.assertEqual(self.track1.genre, "Hard Rock")

    def test_07seventh(self):
        self.assertEqual(self.track1.titlesort, "D1.T09.NNN")

    def test_08eighth(self):
        self.assertIn("taggingtime", self.track1)

    def test_09ninth(self):
        self.assertIn("encodingtime", self.track1)

    def test_10tenth(self):
        self.assertEqual(self.track1.origyear, "1987")

    def test_11eleventh(self):
        self.assertEqual(self.track1.year, "1987")

    def test_12twelfth(self):
        self.assertEqual(self.track2.origyear, "1987")

    def test_13thirteenth(self):
        self.assertEqual(self.track2.year, "2016")

    def test_14fourteenth(self):
        self.assertEqual(self.track2.albumsort, "1.19870000.1.13")


class Test02DefaultCDTrack(unittest.TestCase):
    """
    Test "Applications.AudioCD.shared.RippedCD".
    """
    def setUp(self):

        # Default single CD tags.
        # Both artist and artistsort are identical.
        # "origyear" is not provided.
        tags = {
            "Album": "Abigail",
            "Year": "1987",
            "Disc": "1/1",
            "Label": "Roadrunner Records",
            "UPC": "016861878825",
            "Artist": "King Diamond",
            "AlbumSortCount": "1",
            "Live": "N",
            "_albumart_1_Front Album Cover": r"C:\Users\Xavier\AppData\Local\Temp\dbp49F2.tmp\9.bin",
            "Track": "9/13",
            "Profile": "Default",
            "Rating": "8",
            "Source": "CD (Lossless)",
            "Encoder": "(FLAC 1.3.0)",
            "ArtistSort": "King Diamond",
            "AlbumArtistSort": "King Diamond",
            "AlbumArtist": "King Diamond",
            "Genre": "Rock",
            "InCollection": "Y",
            "TitleLanguage": "English",
            "Bootleg": "N",
            "Title": "A Mansion in Darkness"
        }

        # Default single CD tags.
        # Both "artist" and "artistsort" are identical.
        # "origyear" is provided.
        self.reftags = {
            "_albumart_1_front album cover": r"C:\Users\Xavier\AppData\Local\Temp\dbp49F2.tmp\9.bin",
            "album": "Abigail",
            "albumartist": "King Diamond",
            "albumartistsort": "King Diamond",
            "albumsort": "1.19870000.1.13",
            "artist": "King Diamond",
            "artistsort": "King Diamond",
            "disc": "1",
            "disctotal": "1",
            "encoder": "(FLAC 1.3.0)",
            "encodingyear": "2016",
            "genre": "Hard Rock",
            "incollection": "Y",
            "label": "Roadrunner Records",
            "origyear": "1987",
            "profile": "Default",
            "rating": "8",
            "source": "CD (Lossless)",
            "title": "A Mansion in Darkness",
            "titlelanguage": "English",
            "titlesort": "D1.T09.NNN",
            "track": "9",
            "tracktotal": "13",
            "upc": "016861878825",
            "year": "1987"
        }
        self.otags, self.tags = os.path.join(os.path.expandvars("%TEMP%"), "T09.json"), None
        with tempfile.TemporaryDirectory() as directory:
            itags = os.path.join(directory, "tags.txt")
            with open(itags, mode=shared.WRITE, encoding=shared.UTF16) as fo:
                for k, v in tags.items():
                    fo.write("{0}={1}\n".format(k, v))
            with RippedCD("default", itags):
                pass
        if os.path.exists(self.otags):
            with open(self.otags, encoding=shared.UTF8) as fo:
                self.tags = json.load(fo)

    def test_01first(self):
        self.assertIn("encodedby", self.tags)

    def test_02second(self):
        self.assertIn("encodingtime", self.tags)

    def test_03third(self):
        self.assertIn("taggingtime", self.tags)

    def test_04fourth(self):
        del self.tags["encodedby"]
        del self.tags["encodingtime"]
        del self.tags["taggingtime"]
        self.assertDictEqual(self.tags, self.reftags)


class Test03DefaultCDTrack(unittest.TestCase):
    """
    Test "Applications.AudioCD.shared.rippinglog" for default single CD.
    Both artist and artistsort are identical.
    "origyear" is not provided.
    """
    def setUp(self):
        tags = {
            "Album": "Abigail",
            "Year": "1987",
            "Disc": "1/1",
            "Label": "Roadrunner Records",
            "UPC": "016861878825",
            "Artist": "King Diamond",
            "AlbumSortCount": "1",
            "Live": "N",
            "_albumart_1_Front Album Cover": r"C:\Users\Xavier\AppData\Local\Temp\dbp49F2.tmp\9.bin",
            "Track": "9/13",
            "Profile": "Default",
            "Rating": "8",
            "Source": "CD (Lossless)",
            "Encoder": "(FLAC 1.3.0)",
            "ArtistSort": "King Diamond",
            "AlbumArtistSort": "King Diamond",
            "AlbumArtist": "King Diamond",
            "Genre": "Rock",
            "InCollection": "Y",
            "TitleLanguage": "English",
            "Bootleg": "N",
            "Title": "A Mansion in Darkness"
        }
        self.first, self.second = ["King Diamond", "1987", "Abigail", "Hard Rock", "016861878825", "1.19870000.1", "King Diamond"], None
        with tempfile.TemporaryDirectory() as directory:
            outfile = os.path.join(directory, "rippinglog.json")
            rippinglog(DefaultCDTrack(**{k.lower(): v for k, v in tags.items()}), fil=outfile)
            if os.path.exists(outfile):
                with open(outfile, encoding=shared.UTF8) as fr:
                    self.second = json.load(fr)[0]

    def test_01first(self):
        self.assertTrue(self.second)

    def test_02second(self):
        self.assertListEqual(self.first, self.second)


class Test04DefaultCDTrack(unittest.TestCase):
    """
    Test "Applications.AudioCD.shared.digitalaudiobase" for default single CD.
    Both artist and artistsort are identical.
    "origyear" is not provided.
    """
    def setUp(self):
        tags = {
            "Album": "Abigail",
            "Year": "1987",
            "Disc": "1/1",
            "Label": "Roadrunner Records",
            "UPC": "016861878825",
            "Artist": "King Diamond",
            "AlbumSortCount": "1",
            "Live": "N",
            "_albumart_1_Front Album Cover": r"C:\Users\Xavier\AppData\Local\Temp\dbp49F2.tmp\9.bin",
            "Track": "9/13",
            "Profile": "Default",
            "Rating": "8",
            "Source": "CD (Lossless)",
            "Encoder": "(FLAC 1.3.0)",
            "ArtistSort": "King Diamond",
            "AlbumArtistSort": "King Diamond",
            "AlbumArtist": "King Diamond",
            "Genre": "Rock",
            "InCollection": "Y",
            "TitleLanguage": "English",
            "Bootleg": "N",
            "Title": "A Mansion in Darkness"
        }
        self.first, self.second = ["K.King Diamond.1.19870000.1.D1.T09.NNN", "1.19870000.1", "D1.T09.NNN", "King Diamond", "1987", "Abigail", "Hard Rock", "1", "1", "Roadrunner Records", "9",
                                   "13", "A Mansion in Darkness", "N", "N", "Y", "016861878825", "2016", "English", "1987"], None
        with tempfile.TemporaryDirectory() as directory:
            outfile = os.path.join(directory, "digitalaudiodatabase.json")
            digitalaudiobase(DefaultCDTrack(**{k.lower(): v for k, v in tags.items()}), fil=outfile)
            if os.path.exists(outfile):
                with open(outfile, encoding=shared.UTF8) as fr:
                    self.second = json.load(fr)[0]

    def test_01first(self):
        self.assertTrue(self.second)

    def test_02second(self):
        self.assertListEqual(self.first, self.second)


class Test05DefaultCDTrack(unittest.TestCase):
    """
    Test "Applications.AudioCD.shared.rippinglog" for a multi CDs album.
    Both artist and artistsort are identical.
    "origyear" is provided.
    """
    def setUp(self):
        tags = {
            "Album": "Abigail",
            "Year": "2016",
            "Disc": "1/2",
            "Label": "Roadrunner Records",
            "UPC": "016861878825",
            "Artist": "King Diamond",
            "AlbumSortCount": "1",
            "Live": "N",
            "_albumart_1_Front Album Cover": r"C:\Users\Xavier\AppData\Local\Temp\dbp49F2.tmp\9.bin",
            "Track": "9/13",
            "Profile": "Default",
            "Rating": "8",
            "Source": "CD (Lossless)",
            "Encoder": "(FLAC 1.3.0)",
            "ArtistSort": "King Diamond",
            "AlbumArtistSort": "King Diamond",
            "AlbumArtist": "King Diamond",
            "Genre": "Rock",
            "InCollection": "Y",
            "TitleLanguage": "English",
            "Bootleg": "N",
            "Title": "A Mansion in Darkness",
            "OrigYear": "1987"
        }
        self.first, self.second = ["King Diamond", "2016", "Abigail (1/2)", "Hard Rock", "016861878825", "1.19870000.1", "King Diamond"], None
        with tempfile.TemporaryDirectory() as directory:
            outfile = os.path.join(directory, "rippinglog.json")
            rippinglog(DefaultCDTrack(**{k.lower(): v for k, v in tags.items()}), fil=outfile)
            if os.path.exists(outfile):
                with open(outfile, encoding=shared.UTF8) as fr:
                    self.second = json.load(fr)[0]

    def test_01first(self):
        self.assertTrue(self.second)

    def test_02second(self):
        self.assertListEqual(self.first, self.second)


class TestParser(unittest.TestCase):

    def setUp(self):
        self.arguments = parser.parse_args(["albums", "1", "2", "3", "4", "--album", "the album", "--year", "1987", "--genre", "Hard Rock", "--discs", "2"])

    def test_01first(self):
        self.assertDictEqual(self.arguments.args, {"album": "the album", "year": 1987, "genre": "Hard Rock", "discs": 2})

    def test_02second(self):
        self.assertListEqual(self.arguments.uid, [1, 2, 3, 4])


class TestUpdateTables(unittest.TestCase):

    def setUp(self):
        self.database = shared.DATABASE
        self.newalbum = "the album"
        self.newgenre = "the genre"
        self.row = "47"

    def test_01first(self):
        with tempfile.TemporaryDirectory() as directory:
            dst = os.path.join(directory, os.path.basename(self.database))
            copy(src=self.database, dst=dst)
            arguments = parser.parse_args(["albums", self.row, "--album", self.newalbum])
            self.assertTrue(updatealbum(*arguments.uid, db=dst, **arguments.args))
            conn = sqlite3.connect(dst)
            conn.row_factory = sqlite3.Row
            try:
                for row in conn.execute("SELECT album from albums WHERE rowid=?", (self.row,)):
                    self.assertEqual(row["album"], self.newalbum)
            except AssertionError:
                raise
            finally:
                conn.close()

    def test_02second(self):
        with tempfile.TemporaryDirectory() as directory:
            dst = os.path.join(directory, os.path.basename(self.database))
            copy(src=self.database, dst=dst)
            arguments = parser.parse_args(["albums", self.row, "--genre", self.newgenre])
            self.assertTrue(updatealbum(*arguments.uid, db=dst, **arguments.args))
            conn = sqlite3.connect(dst)
            conn.row_factory = sqlite3.Row
            try:
                for row in conn.execute("SELECT genre from albums WHERE rowid=?", (self.row,)):
                    self.assertEqual(row["genre"], self.newgenre)
            except AssertionError:
                raise
            finally:
                conn.close()


# def testsuite():
#     suite = unittest.TestSuite()
#     # suite.addTests([TestRegex(), TestEnumerateTuplesList(), TestEnumerateSortedListContent(), TestCanFileBeProcessed(), TestDefaultCDTrack()])
#     suite.addTest(TestRegex("test_01first"))
#     return suite
#
#
# if __name__ == "__main__":
#     print("toto")
#     suite = unittest.TestSuite(TestRegex())
#     # suite.addTests([TestRegex(), TestEnumerateTuplesList(), TestEnumerateSortedListContent(), TestCanFileBeProcessed(), TestDefaultCDTrack()])
#     # suite.addTest(unittest.makeSuite(TestRegex))
#     runner = unittest.TextTestRunner(verbosity=2)
#     runner.run(suite)
