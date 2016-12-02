# -*- coding: utf-8 -*-
from ..shared import zipfileparser
import argparse
import unittest
import os


__author__ = 'Xavier ROSSET'


class TestParser(unittest.TestCase):

    def setUp(self):

        # --> Constants.
        destinations = {"documents": os.path.expandvars("%_MYDOCUMENTS%"),
                        "onedrive": os.path.join(os.path.expandvars("%USERPROFILE%"), "OneDrive"),
                        "temp": os.path.expandvars("%TEMP%"),
                        "backup": os.path.expandvars("%_BACKUP%")
                        }

        # --> Classes.
        class GetPath(argparse.Action):

            def __init__(self, option_strings, dest, **kwargs):
                super(GetPath, self).__init__(option_strings, dest, **kwargs)

            def __call__(self, parsobj, namespace, values, option_string=None):
                setattr(namespace, self.dest, destinations[values])

        # --> Functions.
        def validdirectory(d):
            if not os.path.isdir(d):
                raise argparse.ArgumentTypeError('"{0}" is not a valid directory'.format(d))
            if not os.access(d, os.R_OK):
                raise argparse.ArgumentTypeError('"{0}" is not a readable directory'.format(d))
            return d

        # --> Arguments parser.
        self.parser = argparse.ArgumentParser()
        self.parser.add_argument("directory", help="browsed directory", type=validdirectory)
        self.parser.add_argument("archive", help="archive name")
        self.parser.add_argument("destination", help="archive destination", action=GetPath, choices=list(destinations))
        self.parser.add_argument("-e", "--ext", dest="extensions", help="archived extension(s)", nargs="*")

    def test_01first(self):
        arguments = self.parser.parse_args([os.path.expandvars("%_MYDOCUMENTS%"), "documents", "temp", "-e", "txt", "doc"])
        self.assertEqual(arguments.directory, os.path.expandvars("%_MYDOCUMENTS%"))
        self.assertEqual(arguments.archive, "documents")
        self.assertEqual(arguments.destination, os.path.expandvars("%TEMP%"))
        self.assertListEqual(arguments.extensions, ["txt", "doc"])

    def test_02second(self):
        arguments = self.parser.parse_args([os.path.expandvars("%_MYDOCUMENTS%"), "documents", "temp"])
        self.assertEqual(arguments.directory, os.path.expandvars("%_MYDOCUMENTS%"))
        self.assertEqual(arguments.archive, "documents")
        self.assertEqual(arguments.destination, os.path.expandvars("%TEMP%"))
        self.assertIsNone(arguments.extensions)


class TestSecondParser(unittest.TestCase):

    def setUp(self):
        self.documents = os.path.expandvars("%_MYDOCUMENTS%")

    def test_01first(self):
        arguments = zipfileparser.parse_args([self.documents, "temp", "grouped", "documents"])
        self.assertListEqual(arguments.extensions, ["doc", "txt", "pdf", "xav"])

    def test_02second(self):
        arguments = zipfileparser.parse_args([self.documents, "temp", "grouped", "documents", "-e", "doc"])
        self.assertListEqual(arguments.extensions, ["txt", "pdf", "xav"])

    def test_03third(self):
        arguments = zipfileparser.parse_args([self.documents, "temp", "grouped", "documents", "-k", "pdf"])
        self.assertListEqual(arguments.extensions, ["pdf"])

    def test_04fourth(self):
        arguments = zipfileparser.parse_args([self.documents, "temp", "grouped", "documents", "-e", "doc", "txt", "pdf", "xav"])
        self.assertListEqual(arguments.extensions, [])

    def test_05fifth(self):
        arguments = zipfileparser.parse_args([self.documents, "temp", "grouped", "computing"])
        self.assertListEqual(arguments.extensions, ["py", "json", "yaml", "cmd", "css", "xsl"])

    def test_06sixth(self):
        arguments = zipfileparser.parse_args([self.documents, "temp", "grouped", "computing", "-i", "pdf"])
        self.assertListEqual(arguments.extensions, ["py", "json", "yaml", "cmd", "css", "xsl", "pdf"])

    def test_07seventh(self):
        arguments = zipfileparser.parse_args([self.documents, "temp", "grouped", "computing", "-e", "cmd", "-i", "pdf", "txt"])
        self.assertListEqual(arguments.extensions, ["py", "json", "yaml", "css", "xsl", "pdf", "txt"])

    def test_08eigth(self):
        arguments = zipfileparser.parse_args([self.documents, "temp", "grouped", "computing", "-k", "py", "-i", "pdf", "txt"])
        self.assertListEqual(arguments.extensions, ["py", "pdf", "txt"])

    def test_09ninth(self):
        arguments = zipfileparser.parse_args([self.documents, "temp", "grouped", "computing", "documents"])
        self.assertListEqual(arguments.extensions, ["py", "json", "yaml", "cmd", "css", "xsl", "doc", "txt", "pdf", "xav"])

    def test_10tenth(self):
        arguments = zipfileparser.parse_args([self.documents, "temp", "grouped", "computing", "documents", "-e", "doc", "css"])
        self.assertListEqual(arguments.extensions, ["py", "json", "yaml", "cmd", "xsl", "txt", "pdf", "xav"])

    def test_11eleventh(self):
        arguments = zipfileparser.parse_args([self.documents, "temp", "singled", "doc", "pdf", "txt", "css", "abc"])
        self.assertListEqual(arguments.extensions, ["doc", "pdf", "txt", "css", "abc"])
