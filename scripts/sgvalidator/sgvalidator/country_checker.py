import us
import termcolor
from .validator_utils import ValidatorUtils
from .country_detector import CountryDetector
from .abstract_checker import AbstractChecker


class CountryChecker(AbstractChecker):
    def __init__(self, data, debug):
        self.data = data
        self.debug = debug

    def check(self):
        print(termcolor.colored("Checking for data quality issues...", "blue"))
        for index, row in self.data.iterrows():
            self.check_latitude_and_longitude(row)
            if CountryDetector.is_us(row):
                self.check_us_state(row)
                self.check_us_zip(row)
                self.check_us_phone(row)
            elif CountryDetector.is_canada(row):
                self.check_canada_state(row)
                self.check_canada_zip(row)
                self.check_canada_phone(row)
        if not self.debug:
            print(termcolor.colored("No data quality issues found...", "green"))

    def check_us_state(self, row):
        state = row["state"]
        if not ValidatorUtils.is_blank(state) and not us.states.lookup(state.strip()):
            ValidatorUtils.fail("Invalid state: {}".format(state), self.debug)

    def check_us_zip(self, row):
        zip_code = row["zip"]
        if not ValidatorUtils.is_blank(zip_code) and not CountryDetector.is_us_zip(zip_code):
            ValidatorUtils.fail("Invalid zip code: {}".format(zip_code), self.debug)

    def check_us_phone(self, row):
        phone = row["phone"]
        if not ValidatorUtils.is_blank(phone) and not ValidatorUtils.is_valid_phone_number(phone, "US"):
            ValidatorUtils.fail("Invalid phone number: {}".format(phone), self.debug)

    def check_canada_state(self, row):
        state = row["state"]
        if not ValidatorUtils.is_blank(state) and not CountryDetector.is_canada_state(state):
            ValidatorUtils.fail("Invalid Canadian province/territory: {}".format(state), self.debug)

    def check_canada_phone(self, row):
        phone = row["phone"]
        if not ValidatorUtils.is_blank(phone) and not ValidatorUtils.is_valid_phone_number(phone, "CA"):
            ValidatorUtils.fail("Invalid Canadian phone number: {}".format(phone), self.debug)

    def check_canada_zip(self, row):
        zip_code = row["zip"]
        if not ValidatorUtils.is_blank(zip_code) and not CountryDetector.is_canada_zip(zip_code):
            ValidatorUtils.fail("Invalid Canadian postal code: {}".format(zip_code), self.debug)

    def check_latitude_and_longitude(self, row):
        latitude = row["latitude"]
        longitude = row["longitude"]
        if ValidatorUtils.is_blank(latitude) and ValidatorUtils.is_blank(longitude):
            return
        if not ValidatorUtils.is_blank(latitude) and ValidatorUtils.is_blank(longitude):
            ValidatorUtils.fail("latitude without corresponding longitude for row {}".format(row), self.debug)
        if not ValidatorUtils.is_blank(longitude) and ValidatorUtils.is_blank(latitude):
            ValidatorUtils.fail("longitude without corresponding latitude for row {}".format(row), self.debug)
        if not ValidatorUtils.is_number(latitude):
            ValidatorUtils.fail("non-numeric latitude: {}".format(latitude), self.debug)
        elif not (-90.0 <= float(latitude) <= 90.0):
            ValidatorUtils.fail("latitude out of range: {}".format(latitude), self.debug)
        if not ValidatorUtils.is_number(longitude):
            ValidatorUtils.fail("non-numeric longitude: {}".format(longitude), self.debug)
        elif not (-180.0 <= float(longitude) <= 180.0):
            ValidatorUtils.fail("longitude out of range: {}".format(longitude), self.debug)

