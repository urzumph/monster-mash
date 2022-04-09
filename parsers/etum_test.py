import unittest
from . import parser
from . import etum
import pathlib
import json
import re
import char


class TestEtumParser(unittest.TestCase):
    def setUp(self):
        self.maxDiff = None

    tests = ["etum_minotaurchief", "etum_psihulk"]

    def test_parser(self):
        for t in self.tests:
            text = pathlib.Path("tests/" + t + ".txt").read_text()
            tarr = text.split("\n")
            doc = parser.Document(tarr)
            jt = pathlib.Path("tests/" + t + ".json").read_text()
            jres = char.Sheet()
            jres.from_json(jt)
            result = char.Sheet()
            doc.parse(etum.parsers, result)
            self.assertEqual(result, jres, f"Parser results:\n{doc}")


if __name__ == "__main__":
    unittest.main()
