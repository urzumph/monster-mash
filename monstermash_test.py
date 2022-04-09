import unittest
import monstermash
import pathlib
import json
import re
import char


class TestMonsterMash(unittest.TestCase):
    def setUp(self):
        self.maxDiff = None

    tests = ["etum_minotaurchief", "etum_psihulk"]

    def test_parse(self):
        # TODO: Testing of the parsing results makes more sense
        # in the tests of the parsers themselves.
        # This should test logic specific to the monstermash
        # parse function, but it's logic is currently very limited.
        for t in self.tests:
            text = pathlib.Path("tests/" + t + ".txt").read_text()
            tarr = text.split("\n")
            jt = pathlib.Path("tests/" + t + ".json").read_text()
            jres = char.Sheet()
            jres.from_json(jt)
            result = monstermash.parse(tarr)
            self.assertEqual(result, jres)


if __name__ == "__main__":
    unittest.main()
