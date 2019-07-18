from unittest import TestCase
from ..country_checker import CountryChecker

country_checker = CountryChecker(None, debug=False)


class TestCaCountryChecker(TestCase):
    def testCheckCaState(self):
        country_checker.check_canada_state({"state": None})
        country_checker.check_canada_state({"state": "ab"})
        country_checker.check_canada_state({"state": "alberta"})
        country_checker.check_canada_state({"state": " ALBERTA "})
        country_checker.check_canada_state({"state": "quebec"})

        with self.assertRaises(AssertionError):
            country_checker.check_canada_state({"state": "alberta!"})

        with self.assertRaises(AssertionError):
            country_checker.check_canada_state({"state": "newfoundland"})

        with self.assertRaises(AssertionError):
            country_checker.check_canada_state({"state": "price edwardsd"})

    def testCheckCaZip(self):
        country_checker.check_canada_zip({"zip": "A1A 1A1"})
        country_checker.check_canada_zip({"zip": "P0M 0B8"})
        country_checker.check_canada_zip({"zip": "L0N 1R0"})
        country_checker.check_canada_zip({"zip": None})

        with self.assertRaises(AssertionError):
            country_checker.check_canada_zip({"zip": "A1A1A1"})

        with self.assertRaises(AssertionError):
            country_checker.check_canada_zip({"zip": "O1A 1A1"})

    def testCheckCaPhone(self):
        country_checker.check_canada_phone({"phone": "2149260428"})
        country_checker.check_canada_phone({"phone": "+12149260428"})
        country_checker.check_canada_phone({"phone": None})
        country_checker.check_canada_phone({"phone": "+1 (214) 926-0428"})

        with self.assertRaises(AssertionError):
            country_checker.check_canada_phone({"phone": "960428"})

        with self.assertRaises(AssertionError):
            country_checker.check_canada_phone({"phone": "214-926!0428"})

        with self.assertRaises(AssertionError):
            country_checker.check_canada_phone({"phone": "2149260428 null"})
