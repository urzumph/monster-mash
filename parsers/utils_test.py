import unittest
import re
from . import utils


class TestUtils(unittest.TestCase):
    def test_regexiter(self):
        rxi = utils.RegexIter("a=1,b=2,potato", re.compile("(\w)=(\d),?"))
        count = 0
        for m in iter(rxi):
            if count == 0:
                self.assertEqual(m.group(1), "a")
                self.assertEqual(m.group(2), "1")
            if count == 1:
                self.assertEqual(m.group(1), "b")
                self.assertEqual(m.group(2), "2")
            if count > 1:
                self.fail(f"Got unexpected count: {count}")
            count += 1
        self.assertEqual(rxi.remainder, "potato")
