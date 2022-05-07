import unittest
from . import parser
from . import cotsq
import pathlib
import json
import re
import char
import logging


class TestCotsqParser(unittest.TestCase):
    def setUp(self):
        self.maxDiff = None

    tests = ["cotsq_chahir", "cotsq_maurezhi"]

    def test_parser(self):
        logging.debug("Starting Cotsq Parser test")
        for t in self.tests:
            text = pathlib.Path("tests/" + t + ".txt").read_text()
            tarr = text.split("\n")
            doc = parser.Document(tarr)
            jt = pathlib.Path("tests/" + t + ".json").read_text()
            jres = char.Sheet()
            jres.from_json(jt)
            result = char.Sheet()
            logging.debug("Initiating parse of %s with %s", text, cotsq.parsers)
            doc.parse(cotsq.parsers, result)
            logging.debug("Test parse of %s complete", jt)
            self.assertEqual(result, jres, f"Parsed:\n{result}\nParser results:\n{doc}")
        logging.debug("End Cotsq Parser test")


if __name__ == "__main__":
    unittest.main()