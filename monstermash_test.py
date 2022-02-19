import unittest
import monstermash
import pathlib
import json
import re


class TestMonsterMash(unittest.TestCase):
    def test_accum_until(self):
        test = ["ONE", "PURPLE", "TWO\n", "THREE"]
        until = re.compile("^T")
        untilNever = re.compile("^Z")
        resultZero = monstermash.accum_until(0, until, test)
        self.assertEqual(resultZero, "ONE PURPLE")
        resultOne = monstermash.accum_until(1, until, test)
        self.assertEqual(resultOne, "PURPLE")
        resultTwo = monstermash.accum_until(2, untilNever, test)
        self.assertEqual(resultTwo, "TWO THREE")

    def test_prechomp_regex(self):
        test = "ONETWOTHREE"
        regex = re.compile("^ONE")
        resstring, resmatch = monstermash.prechomp_regex(test, regex)
        self.assertEqual(resstring, "TWOTHREE")
        self.assertEqual(resmatch.group(0), "ONE")

    tests = ["etum_minotaurchief", "etum_psihulk"]

    def test_parse(self):
        self.maxDiff = None
        for t in self.tests:
            text = pathlib.Path("tests/" + t + ".txt").read_text()
            tarr = text.split("\n")
            jt = pathlib.Path("tests/" + t + ".json").read_text()
            jres = json.loads(jt)
            result = monstermash.parse(tarr)
            self.assertDictEqual(result, jres)


if __name__ == "__main__":
    unittest.main()
