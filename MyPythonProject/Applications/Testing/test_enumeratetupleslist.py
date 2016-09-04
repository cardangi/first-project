# -*- coding: ISO-8859-1 -*-
from unittest import TestCase
from Applications import shared

__author__ = 'Xavier ROSSET'


class TestEnumeratetupleslist(TestCase):

    def test_first(self):
        self.assertEqual([(1, "path1", "file1"), (2, "path2", "file2"), (3, "path3", "file3"), (4, "path4", "file4"), (5, "path6", "file6")], shared.enumeratetupleslist([("path1", "file1"),
                                                                                                                                                                          ("path2", "file2"),
                                                                                                                                                                          ("path3", "file3"),
                                                                                                                                                                          ("path6", "file6"),
                                                                                                                                                                          ("path4", "file4")
                                                                                                                                                                          ])
                         )
