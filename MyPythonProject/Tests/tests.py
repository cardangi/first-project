# -*- coding: ISO-8859-1 -*-
import os
import json
import yaml
import unittest
import tempfile
from Applications import shared
from Applications.AudioCD.shared import DefaultCDTrack, RippedCD, canfilebeprocessed, digitalaudiobase, rippinglog

__author__ = 'Xavier ROSSET'


class TestRegex(unittest.TestCase):

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

    def setUp(self):

        # Default single CD tags.
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

        # Single CD tags. Both "year" and "origyear" are provided.
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

    def setUp(self):

        # Default single CD tags.
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

        # Default expected tags.
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
        self.otags = os.path.join(os.path.expandvars("%TEMP%"), "T09.yml")
        with tempfile.TemporaryDirectory() as dir:
            itags = os.path.join(dir, "tags.txt")
            with open(itags, mode=shared.WRITE, encoding=shared.UTF16) as fo:
                for k, v in tags.items():
                    fo.write("{0}={1}\n".format(k, v))
            with RippedCD("default", itags):
                pass

    @unittest.skipIf(not os.path.exists(os.path.join(os.path.expandvars("%TEMP%"), "T09.yml")), "Reference tags file doesn\'t exist")
    def test_01first(self):
        with open(self.otags) as fo:
            self.assertIn("encodedby", yaml.load(fo))

    @unittest.skipIf(not os.path.exists(os.path.join(os.path.expandvars("%TEMP%"), "T09.yml")), "Reference tags file doesn\'t exist")
    def test_02second(self):
        with open(self.otags) as fo:
            self.assertIn("encodingtime", yaml.load(fo))

    @unittest.skipIf(not os.path.exists(os.path.join(os.path.expandvars("%TEMP%"), "T09.yml")), "Reference tags file doesn\'t exist")
    def test_03third(self):
        with open(self.otags) as fo:
            self.assertIn("taggingtime", yaml.load(fo))

    @unittest.skipIf(not os.path.exists(os.path.join(os.path.expandvars("%TEMP%"), "T09.yml")), "Reference tags file doesn\'t exist")
    def test_04fourth(self):
        with open(self.otags) as fo:
            rippedcd = yaml.load(fo)
        del rippedcd["encodedby"]
        del rippedcd["encodingtime"]
        del rippedcd["taggingtime"]
        self.assertDictEqual(rippedcd, self.reftags)


class Test03DefaultCDTrack(unittest.TestCase):
    # Test "Applications.AudioCD.shared.rippinglog" for default single CD.

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
        with tempfile.TemporaryDirectory() as dir:
            outfile = os.path.join(dir, "rippinglog.json")
            rippinglog(DefaultCDTrack(**{k.lower(): v for k, v in tags.items()}), fil=outfile)
            if os.path.exists(outfile):
                with open(outfile) as fr:
                    self.second = json.load(fr)[0]

    def test_01first(self):
        self.assertTrue(self.second)

    def test_02second(self):
        self.assertListEqual(self.first, self.second)


class Test04DefaultCDTrack(unittest.TestCase):
    # Test "Applications.AudioCD.shared.digitalaudiobase" for default single CD.

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
        with tempfile.TemporaryDirectory() as dir:
            outfile = os.path.join(dir, "digitalaudiodatabase.json")
            digitalaudiobase(DefaultCDTrack(**{k.lower(): v for k, v in tags.items()}), fil=outfile)
            if os.path.exists(outfile):
                with open(outfile) as fr:
                    self.second = json.load(fr)[0]

    def test_01first(self):
        self.assertTrue(self.second)

    def test_02second(self):
        self.assertListEqual(self.first, self.second)


class Test05DefaultCDTrack(unittest.TestCase):
    # Test "Applications.AudioCD.shared.rippinglog" for default multi CD.

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
        with tempfile.TemporaryDirectory() as dir:
            outfile = os.path.join(dir, "rippinglog.json")
            rippinglog(DefaultCDTrack(**{k.lower(): v for k, v in tags.items()}), fil=outfile)
            if os.path.exists(outfile):
                with open(outfile) as fr:
                    self.second = json.load(fr)[0]

    def test_01first(self):
        self.assertTrue(self.second)

    def test_02second(self):
        self.assertListEqual(self.first, self.second)


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
