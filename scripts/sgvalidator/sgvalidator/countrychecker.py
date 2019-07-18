import us
from .validatorutils import ValidatorUtils
from .countrydetector import CountryDetector


class CountryChecker:
    def __init__(self, debug):
        self.debug = debug

    def check_us_state(self, row):
        state = row["state"]
        if not ValidatorUtils.is_blank(state) and not us.states.lookup(state.strip()):
            ValidatorUtils.fail("invalid state: {}".format(state), self.debug)

    def check_us_zip(self, row):
        zip_code = row["zip"]
        if not ValidatorUtils.is_blank(zip_code) and not CountryDetector.is_us_zip(zip_code):
            ValidatorUtils.fail("invalid zip code: {}".format(zip_code), self.debug)

    def check_us_phone(self, row):
        phone = row["phone"]
        if not ValidatorUtils.is_blank(phone) and not ValidatorUtils.is_valid_phone_number(phone, "US"):
            ValidatorUtils.fail("invalid phone number: {}".format(phone), self.debug)

    def check_canada_state(self, row):
        state = row["state"]
        if not ValidatorUtils.is_blank(state) and not CountryDetector.is_canada_state(state):
            ValidatorUtils.fail("invalid Canadian province/territory: {}".format(state), self.debug)

    def check_canada_phone(self, row):
        phone = row["phone"]
        if not ValidatorUtils.is_blank(phone) and not ValidatorUtils.is_valid_phone_number(phone, "CA"):
            ValidatorUtils.fail("invalid Canadian phone number: {}".format(phone), self.debug)

    def check_canada_zip(self, row):
        zip_code = row["zip"]
        if not ValidatorUtils.is_blank(zip_code) and not CountryDetector.is_canada_zip(zip_code):
            ValidatorUtils.fail("invalid Canadian postal code: {}".format(zip_code), self.debug)
