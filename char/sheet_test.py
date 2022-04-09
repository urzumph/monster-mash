import unittest
import pathlib
import json
import re
import parsers
from . import sheet


class TestSheet(unittest.TestCase):
    def test_check_assignment(self):
        s = sheet.Sheet()
        with self.assertRaises(TypeError):
            s._check_assignment("potato", "is potato")
        with self.assertRaises(ValueError):
            s._check_assignment("name", dict())
        val = "   ManySpaces   "
        self.assertEqual(s._check_assignment("name", val), "ManySpaces")

    def test_set_read(self):
        # Basic Test
        s = sheet.Sheet()
        val = "NameValue"
        s["name"] = val
        self.assertEqual(s["name"], val)
        # TODO: Test append when we have a data type for that
        # Subsheet test
        s["ac"]["base"] = 10
        self.assertEqual(s["ac"]["base"], "10")
        # Subsheet wildcard test
        s["skills"]["potato"] = "11"
        self.assertEqual(s["skills"]["potato"], "11")

    def test_read_failure(self):
        s = sheet.Sheet()
        with self.assertRaises(KeyError):
            test = s["invalid"]


if __name__ == "__main__":
    unittest.main()
