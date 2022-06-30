import unittest
from parsers import parser
import pathlib
import json
import re
import char
import logging


class ParserTest(unittest.TestCase):
    def setUp(self):
        self.maxDiff = None

    name = "ParentClass_DoNotInstanciate"
    parsers = []
    tests = []

    def test_parser(self):
        logging.debug(f"Starting {self.name} Parser Test")
        for t in self.tests:
            text = pathlib.Path("tests/" + t + ".txt").read_text()
            tarr = text.split("\n")
            doc = parser.Document(tarr)
            jt = pathlib.Path("tests/" + t + ".json").read_text()
            jres = char.Sheet()
            jres.from_json(jt)
            result = char.Sheet()
            logging.debug("Initiating parse of %s with %s", text, self.parsers)
            doc.parse(self.parsers, result)
            logging.debug("Test parse of %s complete", jt)
            reason = jres.compare(result)
            self.assertEqual(
                result,
                jres,
                f"Parsed:\n{result}\nParser results:\n{doc}\nComparison:\n{reason}\n(lhs=json, rhs=parser output)",
            )
        logging.debug(f"End {self.name} Parser Test")


if __name__ == "__main__":
    unittest.main()
