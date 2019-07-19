import pandas as pd
from .utils import getFakeData
from unittest import TestCase
from ..duplication_checker import DuplicationChecker

data = pd.DataFrame(getFakeData())
debugChecker = DuplicationChecker(data, debug=True)
nonDebugChecker = DuplicationChecker(data, debug=False)


class TestDuplicationChecker(TestCase):
    def testCheckIdentityDuplication(self):
        self.assertTrue(len(debugChecker.checkForIdentityDuplicates() == 3))
        with self.assertRaises(AssertionError):
            nonDebugChecker.check()

    def testCheckLatLngDuplication(self):
        self.assertTrue(len(debugChecker.checkLatLngsWithMultipleAddresses() == 1))
        with self.assertRaises(AssertionError):
            nonDebugChecker.check()

    def testWarnIfSameAddrHasMultipleLatLngs(self):
        res = debugChecker.warnIfSameAddrHasMultipleLatLngs()
        self.assertTrue(len(res) == 2)