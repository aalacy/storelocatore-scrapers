from .utils import getFakeData
from unittest import TestCase
from ..fillratechecker import FillRateChecker


class TestTrashValueChecker(TestCase):
    def testFindTrashValues(self):
        fakeData = getFakeData("testdata_some_columns_null.csv")
        dataCount = len(fakeData)
        nullCountsByColumn = FillRateChecker.checkFillRate(fakeData)
        concerningCols = sorted([k for k, v in nullCountsByColumn.items() if 100.0 * v / dataCount > FillRateChecker.PERC_CUTOFF])
        expectedConcerningCols = sorted(["zip", "addr", "location_type"])
        self.assertEqual(concerningCols, expectedConcerningCols)
