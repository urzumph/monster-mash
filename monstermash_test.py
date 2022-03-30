import unittest
import monstermash
import pathlib
import json
import re


class TestMonsterMash(unittest.TestCase):
    def setUp(self):
        self.maxDiff = None

    tests = ["etum_minotaurchief", "etum_psihulk"]

    def test_parse(self):
        for t in self.tests:
            text = pathlib.Path("tests/" + t + ".txt").read_text()
            tarr = text.split("\n")
            jt = pathlib.Path("tests/" + t + ".json").read_text()
            jres = json.loads(jt)
            result = monstermash.parse(tarr)
            self.assertDictEqual(result, jres)


if __name__ == "__main__":
    unittest.main()
