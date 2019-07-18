import pandas as pd
from .utils import getFakeData
from unittest import TestCase
from ..duplication_checker import DuplicationChecker


class TestDuplicationChecker(TestCase):
    def testCheckDuplication(self):
        data = pd.DataFrame(getFakeData())
        checker = DuplicationChecker(data, debug=False)
        self.assertTrue(len(checker.getDuplicateRows(checker.data, checker.keys)) == 3)
        with self.assertRaises(AssertionError):
            checker.check()