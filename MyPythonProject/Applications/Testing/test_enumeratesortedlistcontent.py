# -*- coding: ISO-8859-1 -*-
from unittest import TestCase
from Applications import shared

__author__ = 'Xavier ROSSET'


class TestEnumeratesortedlistcontent(TestCase):

    def test_first(self):
        self.assertEqual([(1, "path1"), (2, "path2"), (3, "path3"), (4, "path4"), (5, "path6")], shared.enumeratesortedlistcontent(["path1", "path2", "path3", "path6", "path4"]))
