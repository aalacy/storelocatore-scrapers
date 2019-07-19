import pandas as pd
from .utils import getFakeData
from unittest import TestCase
from ..schema_checker import SchemaChecker


class TestValidate(TestCase):
    def testCheckSchema(self):
        goodData = getFakeData('sample_data_good_header.csv')
        checkerGood = SchemaChecker(pd.DataFrame(goodData), goodData, debug=False)
        checkerGood.check()

        badData = getFakeData('sample_data_bad_header.csv')
        checkerBad = SchemaChecker(pd.DataFrame(badData), badData, debug=False)

        self.assertTrue(len(checkerGood.getRequiredColumnsThatArentInData()) == 0)
        self.assertTrue(checkerBad.getRequiredColumnsThatArentInData() == {"street_address", "state"})
        with self.assertRaises(AssertionError):
            checkerBad.check()

