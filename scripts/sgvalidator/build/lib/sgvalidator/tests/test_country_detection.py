from unittest import TestCase
from ..country_detector import CountryDetector


class TestCountryDetection(TestCase):
    def testFixCountry(self):
        self.assertTrue(CountryDetector.fix_country("US") == "us")
        self.assertTrue(CountryDetector.fix_country("united states") == "us")
        self.assertTrue(CountryDetector.fix_country("CA") == "ca")
        self.assertTrue(CountryDetector.fix_country("can") == "ca")
        self.assertTrue(CountryDetector.fix_country("") == None)
        self.assertTrue(CountryDetector.fix_country(None) == None)
        self.assertTrue(CountryDetector.fix_country("Fake  ") == "fake")

    def testIsUsZip(self):
        self.assertTrue(CountryDetector.is_us_zip("94103"))
        self.assertTrue(CountryDetector.is_us_zip("94103-1234"))
        self.assertTrue(CountryDetector.is_us_zip("00000"))

        self.assertFalse(CountryDetector.is_us_zip("9104"))
        self.assertFalse(CountryDetector.is_us_zip(None))
        self.assertFalse(CountryDetector.is_us_zip("910421-1234"))
        self.assertFalse(CountryDetector.is_us_zip("342131"))

    def testIsCountry(self):
        self.assertTrue(CountryDetector.is_us({"country_code": "united states"}))
        self.assertTrue(CountryDetector.is_us({"country_code": None, "zip": "12345"}))
        self.assertTrue(CountryDetector.is_us({"country_code": None, "zip": None, "state": "tx"}))
        self.assertTrue(CountryDetector.is_canada({"country_code": "can"}))
        self.assertTrue(CountryDetector.is_canada({"country_code": None, "zip": "A1A 1A1"}))
        self.assertTrue(CountryDetector.is_canada({"country_code": None, "zip": None, "state": "ab"}))
