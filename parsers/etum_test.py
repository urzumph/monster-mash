import unittest
from . import parser
from . import etum
import pathlib
import json
import re


class TestEtumParser(unittest.TestCase):
    def setUp(self):
        self.maxDiff = None

    tests = ["etum_minotaurchief", "etum_psihulk"]

    # TODO: ng parser still missing a bunch of parsing options
    @unittest.expectedFailure
    def test_ng_parser(self):
        for t in self.tests:
            text = pathlib.Path("tests/" + t + ".txt").read_text()
            tarr = text.split("\n")
            doc = parser.Document(tarr)
            jt = pathlib.Path("tests/" + t + ".json").read_text()
            jres = json.loads(jt)
            # TODO: Fix when I implement character sheets properly
            result = dict()
            result["skills"] = dict()
            result["ac"] = dict()
            result["saves"] = dict()
            result["abilities"] = dict()
            result["moves"] = []
            doc.parse(etum.parsers, result)
            self.assertDictEqual(result, jres, f"Parser results:\n{doc}")


if __name__ == "__main__":
    unittest.main()
