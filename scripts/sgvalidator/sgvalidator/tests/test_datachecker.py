import pandas as pd
from .utils import getFakeData
from unittest import TestCase
from ..duplicationchecker import DuplicationChecker
from ..schemachecker import SchemaChecker
from ..coordinateschecker import CoordinatesChecker


class TestValidate(TestCase):
    def testCheckSchema(self):
        data = getFakeData('testdata_goodheader.csv')
        SchemaChecker(pd.DataFrame(data), data, debug=False).check()
        with self.assertRaises(AssertionError):
            data = getFakeData('testdata_badheader.csv')
            SchemaChecker(pd.DataFrame(data), data, debug=False).check()

    def testCheckDuplication(self):
        with self.assertRaises(AssertionError):
            DuplicationChecker(pd.DataFrame(getFakeData()), debug=False).check()

    def testLatitudeAndLongitude(self):
        coordinatesChecker = CoordinatesChecker(debug=False)
        coordinatesChecker.check_latitude_and_longitude({"latitude": "37.12334", "longitude": "122.123213"})
        coordinatesChecker.check_latitude_and_longitude({"latitude": "-29.12334", "longitude": "122.123213"})
        coordinatesChecker.check_latitude_and_longitude({"latitude": "29.12334", "longitude": "-122.123213"})
        coordinatesChecker.check_latitude_and_longitude({"latitude": "-37.12334", "longitude": "-122.123213"})

        with self.assertRaises(AssertionError):
            coordinatesChecker.check_latitude_and_longitude({"latitude": "0.0", "longitude": None})

        with self.assertRaises(AssertionError):
            coordinatesChecker.check_latitude_and_longitude({"latitude": None, "longitude": "0.0"})

        with self.assertRaises(AssertionError):
            coordinatesChecker.check_latitude_and_longitude({"latitude": "37", "longitude": "-122 longitude"})

        with self.assertRaises(AssertionError):
            coordinatesChecker.check_latitude_and_longitude({"latitude": "37 lat", "longitude": "-122"})

        with self.assertRaises(AssertionError):
            coordinatesChecker.check_latitude_and_longitude({"latitude": "-91", "longitude": "-122"})

        with self.assertRaises(AssertionError):
            coordinatesChecker.check_latitude_and_longitude({"latitude": "-89", "longitude": "-181"})
