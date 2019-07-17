import os
import csv
from unittest import TestCase
from ..datachecker import DataChecker
import zipcodes


def fakeData(fname='testdata_goodheader.csv'):
    data = []
    path = os.path.join(os.path.dirname(__file__), fname)
    with open(path) as csv_file:
        reader = csv.DictReader(csv_file, skipinitialspace=True)
        for row in reader:
            data.append(row)
    return data


class TestValidate(TestCase):
    def testCheckSchema(self):
        DataChecker(fakeData('testdata_goodheader.csv'), debug=False).check_schema()
        with self.assertRaises(AssertionError):
            DataChecker(fakeData('testdata_badheader.csv'), debug=False).check_schema()

    def testCheckDuplication(self):
        checker = DataChecker(fakeData(), debug=False)
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
