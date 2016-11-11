# -*- coding: ISO-8859-1 -*-
import unittest
from Applications import shared as s1
from Applications.CDRipper.Modules import shared as s2

__author__ = 'Xavier ROSSET'


class TestRegexes(unittest.TestCase):

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


class TestEnumeratetupleslist(unittest.TestCase):

    def test_01first(self):
        self.assertEqual([(1, "path1", "file1"), (2, "path2", "file2"), (3, "path3", "file3"), (4, "path4", "file4"), (5, "path6", "file6")], s1.enumeratetupleslist([("path1", "file1"),
                                                                                                                                                                          ("path2", "file2"),
                                                                                                                                                                          ("path3", "file3"),
                                                                                                                                                                          ("path6", "file6"),
                                                                                                                                                                          ("path4", "file4")
                                                                                                                                                                          ])
                         )


class TestEnumeratesortedlistcontent(unittest.TestCase):

    def test_01first(self):
        self.assertEqual([(1, "path1"), (2, "path2"), (3, "path3"), (4, "path4"), (5, "path6")], s1.enumeratesortedlistcontent(["path1", "path2", "path3", "path6", "path4"]))


class TestCanfilebeprocessed(unittest.TestCase):

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


def testsuite():
    suite = unittest.TestSuite()
    suite.addTests([TestRegexes(), TestEnumeratetupleslist(), TestEnumeratesortedlistcontent(), TestCanfilebeprocessed()])
    return suite


if __name__ == "__main__":
    runner = unittest.TextTestRunner()
    runner.run(testsuite())
