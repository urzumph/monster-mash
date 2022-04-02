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

    # Temporary test to verify all needed attributes etc
    @unittest.expectedFailure
    def test_parse(self):
        t = "etum_minotaurchief"
        text = pathlib.Path("tests/" + t + ".txt").read_text()
        tarr = text.split("\n")
        jt = pathlib.Path("tests/" + t + ".json").read_text()
        jres = json.loads(jt)

        result = sheet.Sheet()
        doc = parsers.Document(tarr)
        doc.parse(parsers.etum_mode, result)
        self.assertDictEqual(result, jres)


if __name__ == "__main__":
    unittest.main()
