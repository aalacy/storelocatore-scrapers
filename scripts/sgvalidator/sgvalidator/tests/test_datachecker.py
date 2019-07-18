from .utils import getFakeData
from unittest import TestCase
from ..datachecker import DataChecker


class TestValidate(TestCase):
    def testCheckSchema(self):
        DataChecker(getFakeData('testdata_goodheader.csv'), debug=False).check_schema()
        with self.assertRaises(AssertionError):
            DataChecker(getFakeData('testdata_badheader.csv'), debug=False).check_schema()

    def testCheckDuplication(self):
        checker = DataChecker(getFakeData(), debug=False)
        with self.assertRaises(AssertionError):
            checker.check_duplication()

    def testLatitudeAndLongitude(self):
        checker = DataChecker(None, debug=False)
        checker.check_latitude_and_longitude({"latitude": "37.12334", "longitude": "122.123213"})
        checker.check_latitude_and_longitude({"latitude": "-29.12334", "longitude": "122.123213"})
        checker.check_latitude_and_longitude({"latitude": "29.12334", "longitude": "-122.123213"})
        checker.check_latitude_and_longitude({"latitude": "-37.12334", "longitude": "-122.123213"})

        with self.assertRaises(AssertionError):
            checker.check_latitude_and_longitude({"latitude": "0.0", "longitude": None})

        with self.assertRaises(AssertionError):
            checker.check_latitude_and_longitude({"latitude": None, "longitude": "0.0"})

        with self.assertRaises(AssertionError):
            checker.check_latitude_and_longitude({"latitude": "37", "longitude": "-122 longitude"})

        with self.assertRaises(AssertionError):
            checker.check_latitude_and_longitude({"latitude": "37 lat", "longitude": "-122"})

        with self.assertRaises(AssertionError):
            checker.check_latitude_and_longitude({"latitude": "-91", "longitude": "-122"})

        with self.assertRaises(AssertionError):
            checker.check_latitude_and_longitude({"latitude": "-89", "longitude": "-181"})
