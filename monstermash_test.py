import unittest
import monstermash
import pathlib
import json
import re
import char


class TestMonsterMash(unittest.TestCase):
    def setUp(self):
        self.maxDiff = None

    tests = ["etum_minotaurchief", "etum_psihulk", "cotsq_chahir", "cotsq_maurezhi"]

    def test_parse(self):
        # Moreso than the parsing itself, this tests the automatic type detection.
        for t in self.tests:
            text = pathlib.Path("tests/" + t + ".txt").read_text()
            tarr = text.split("\n")
            jt = pathlib.Path("tests/" + t + ".json").read_text()
            jres = char.Sheet()
            jres.from_json(jt)
            result = monstermash.parse(tarr)
            reason = jres.compare(result)
            self.assertEqual(
                result,
                jres,
                f"Failure in test {t}:\nParsed:\n{result}\nComparison:\n{reason}",
            )


if __name__ == "__main__":
    unittest.main()
