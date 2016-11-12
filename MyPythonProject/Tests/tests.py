# -*- coding: ISO-8859-1 -*-
import unittest
from Applications import shared as s1
from Applications.AudioCD import shared as s2

__author__ = 'Xavier ROSSET'


class TestRegex(unittest.TestCase):

    def test_01first(self):
        self.assertRegex("1.19840000.1.13", r"^(?=1\.\d[\d.]+$)(?=[\d.]+\.13$)1\.(?:{0})0000\.\d\.13$".format(s1.DFTYEARREGEX))

    def test_02second(self):
        self.assertNotRegex("1.19840000.1.15", r"^(?=1\.\d[\d.]+$)(?=[\d.]+\.13$)1\.(?:{0})0000\.\d\.13$".format(s1.DFTYEARREGEX))

    def test_03third(self):
        self.assertNotRegex("1.19840000.1", r"^(?=1\.\d[\d.]+$)(?=[\d.]+\.13$)1\.(?:{0})0000\.\d\.13$".format(s1.DFTYEARREGEX))

    def test_04fourth(self):
        self.assertNotRegex("2.20160529.1.13", r"^(?=1\.\d[\d.]+$)(?=[\d.]+\.13$)1\.(?:{0})0000\.\d\.13$".format(s1.DFTYEARREGEX))

    def test_05fifth(self):
        self.assertNotRegex("2.99999999.1.13", r"^(?=1\.\d[\d.]+$)(?=[\d.]+\.13$)1\.(?:{0})0000\.\d\.13$".format(s1.DFTYEARREGEX))

    def test_06sixth(self):
        self.assertRegex("1994.1 - Dissident", r"^(?:{0})\.\d -\B".format(s1.DFTYEARREGEX))

    def test_07seventh(self):
        self.assertNotRegex("Dissident", r"^(?:{0})\.\d -\B".format(s1.DFTYEARREGEX))

    def test_08eighth(self):
        self.assertNotRegex("1994 - Dissident", r"^(?:{0})\.\d -\B".format(s1.DFTYEARREGEX))


class TestEnumerateTuplesList(unittest.TestCase):

    def test_01first(self):
        self.assertEqual([(1, "path1", "file1"), (2, "path2", "file2"), (3, "path3", "file3"), (4, "path4", "file4"), (5, "path6", "file6")], s1.enumeratetupleslist([("path1", "file1"),
                                                                                                                                                                      ("path2", "file2"),
                                                                                                                                                                      ("path3", "file3"),
                                                                                                                                                                      ("path6", "file6"),
                                                                                                                                                                      ("path4", "file4")
                                                                                                                                                                      ])
                         )


class TestEnumerateSortedListContent(unittest.TestCase):

    def test_01first(self):
        self.assertEqual([(1, "path1"), (2, "path2"), (3, "path3"), (4, "path4"), (5, "path6")], s1.enumeratesortedlistcontent(["path1", "path2", "path3", "path6", "path4"]))


class TestCanFileBeProcessed(unittest.TestCase):

    def test_01first(self):
        self.assertTrue(s2.canfilebeprocessed("flac", *()))

    def test_02second(self):
        self.assertFalse(s2.canfilebeprocessed("pdf", *()))

    def test_03third(self):
        self.assertTrue(s2.canfilebeprocessed("flac", *("flac",)))

    def test_04fourth(self):
        self.assertFalse(s2.canfilebeprocessed("mp3", *("flac",)))

    def test_05fifth(self):
        self.assertFalse(s2.canfilebeprocessed("flac", *("pdf",)))

    def test_06sixth(self):
        self.assertTrue(s2.canfilebeprocessed("FLAC", *()))

    def test_07seventh(self):
        self.assertFalse(s2.canfilebeprocessed("PDF", *()))

    def test_08eighth(self):
        self.assertTrue(s2.canfilebeprocessed("FLAC", *("flac",)))

    def test_09ninth(self):
        self.assertTrue(s2.canfilebeprocessed("flac", *("FLAC",)))

    def test_10tenth(self):
        self.assertTrue(s2.canfilebeprocessed("FLAC", *("FLAC",)))


class TestDefaultCDTrack(unittest.TestCase):

    def setUp(self):
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
        self.track1 = s2.DefaultCDTrack(**{k.lower(): v for k, v in tags1.items()})
        self.track2 = s2.DefaultCDTrack(**{k.lower(): v for k, v in tags2.items()})

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
