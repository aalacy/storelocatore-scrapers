import pandas as pd
from .utils import getFakeData
from unittest import TestCase
from ..fillratechecker import FillRateChecker


class TestTrashValueChecker(TestCase):
    def testFindTrashValues(self):
        fakeData = pd.DataFrame(getFakeData("testdata_some_columns_null.csv"))
        percBlankDf = fakeData.apply(lambda x: x == "", axis=0).mean() * 100
        nullCountsByColumn = FillRateChecker.checkInner(percBlankDf, "blank")
        expectedConcerningCols = sorted(["zip", "addr", "location_type"])
        self.assertEqual(sorted(list(nullCountsByColumn.index)), expectedConcerningCols)
