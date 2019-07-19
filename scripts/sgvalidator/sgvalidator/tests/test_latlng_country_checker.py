from unittest import TestCase
from ..country_checker import CountryChecker


class TestLatLngCountryChecker(TestCase):
    def testLatitudeAndLongitude(self):
        countryChecker = CountryChecker(None, debug=False)
        countryChecker.check_latitude_and_longitude({"latitude": "37.12334", "longitude": "122.123213"})
        countryChecker.check_latitude_and_longitude({"latitude": "-29.12334", "longitude": "122.123213"})
        countryChecker.check_latitude_and_longitude({"latitude": "29.12334", "longitude": "-122.123213"})
        countryChecker.check_latitude_and_longitude({"latitude": "-37.12334", "longitude": "-122.123213"})

        with self.assertRaises(AssertionError):
            countryChecker.check_latitude_and_longitude({"latitude": "0.0", "longitude": None})

        with self.assertRaises(AssertionError):
            countryChecker.check_latitude_and_longitude({"latitude": None, "longitude": "0.0"})

        with self.assertRaises(AssertionError):
            countryChecker.check_latitude_and_longitude({"latitude": "37", "longitude": "-122 longitude"})

        with self.assertRaises(AssertionError):
            countryChecker.check_latitude_and_longitude({"latitude": "37 lat", "longitude": "-122"})

        with self.assertRaises(AssertionError):
            countryChecker.check_latitude_and_longitude({"latitude": "-91", "longitude": "-122"})

        with self.assertRaises(AssertionError):
            countryChecker.check_latitude_and_longitude({"latitude": "-89", "longitude": "-181"})
