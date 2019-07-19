from unittest import TestCase
from ..country_checker import CountryChecker

country_checker = CountryChecker(None, False)


class TestUsCountryChecker(TestCase):
    def testCheckUsState(self):
        country_checker.check_us_state({"state": None})
        country_checker.check_us_state({"state": "ca"})
        country_checker.check_us_state({"state": "CA"})
        country_checker.check_us_state({"state": "California"})
        country_checker.check_us_state({"state": "TX"})
        country_checker.check_us_state({"state": "texas"})

        with self.assertRaises(AssertionError):
            country_checker.check_us_state({"state": "tsxs"})

        with self.assertRaises(AssertionError):
            country_checker.check_us_state({"state": "asds"})

        with self.assertRaises(AssertionError):
            country_checker.check_us_state({"state": "cali"})

        with self.assertRaises(AssertionError):
            country_checker.check_us_state({"state": "sada"})

    def testCheckUsZip(self):
        country_checker.check_us_zip({"zip": "94103"})
        country_checker.check_us_zip({"zip": "94103-1234"})
        country_checker.check_us_zip({"zip": None})

        # note - currently, this zip code doesn't fail because we're
        # not checking against a database of real US zips
        country_checker.check_us_zip({"zip": "00000"})

        with self.assertRaises(AssertionError):
            country_checker.check_us_zip({"zip": "9104"})

        with self.assertRaises(AssertionError):
            country_checker.check_us_zip({"zip": "910421-1234"})

        with self.assertRaises(AssertionError):
            country_checker.check_us_zip({"zip": "342131"})

    def testCheckUsPhone(self):
        country_checker.check_us_phone({"phone": "2149260428"})
        country_checker.check_us_phone({"phone": "+12149260428"})
        country_checker.check_us_phone({"phone": None})
        country_checker.check_us_phone({"phone": "+1 (214) 926-0428"})

        with self.assertRaises(AssertionError):
            country_checker.check_us_phone({"phone": "960428"})

        with self.assertRaises(AssertionError):
            country_checker.check_us_phone({"phone": "214-926!0428"})

        with self.assertRaises(AssertionError):
            country_checker.check_us_phone({"phone": "2149260428 null"})
