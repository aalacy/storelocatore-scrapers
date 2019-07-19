import re
import us
from .validator_utils import *


class CountryDetector:
    @staticmethod
    def fix_country(raw_country):
        if ValidatorUtils.is_blank(raw_country):
            return None
        normalized = raw_country.strip().lower()
        if normalized in ["us", "usa", "united states", "united states of america"]:
            return "us"
        elif normalized in ["ca", "can", "canada"]:
            return "ca"
        else:
            return normalized

    @staticmethod
    def is_us_zip(zip_code):
        cleaned_zip = str(zip_code).strip()
        if ValidatorUtils.is_blank(cleaned_zip):
            return False
        firstpart = cleaned_zip.split("-")[0]
        if len(firstpart) == 5 and ValidatorUtils.is_number(firstpart):
            return True
        else:
            return False

    @staticmethod
    def is_canada_zip(zip_code):
        pattern = re.compile("^[ABCEGHJ-NPRSTVXY][0-9][ABCEGHJ-NPRSTV-Z] [0-9][ABCEGHJ-NPRSTV-Z][0-9]$")
        return zip_code and pattern.match(zip_code)

    @staticmethod
    def is_us_state(state):
        return bool(us.states.lookup(state))

    @staticmethod
    def is_canada_state(state):
        return not ValidatorUtils.is_blank(state) and state.strip().lower() in ['ab', 'alberta', 'bc', 'british columbia',
                                                                 'mb', 'manitoba', 'nb', 'new brunswick', 'nl',
                                                                 'newfoundland and labrador', 'nt',
                                                                 'northwest territories', 'ns', 'nova scotia', 'nu',
                                                                 'nunavut', 'on', 'ontario', 'pe',
                                                                 'prince edward island', 'qc', 'quebec', 'sk',
                                                                 'saskatchewan', 'yt', 'yukon']

    @staticmethod
    def is_us_phone(phone):
        try:
            return phonenumbers.is_valid_number(phonenumbers.parse(phone, "US"))
        except:
            return False

    @staticmethod
    def is_canada_phone(phone):
        try:
            return phonenumbers.is_valid_number(phonenumbers.parse(phone, "CA"))
        except:
            return False

    @staticmethod
    def is_us(row):
        country = CountryDetector.fix_country(row["country_code"])
        if country == "us":
            return True
        elif not ValidatorUtils.is_blank(country):
            return False
        elif row["zip"] and CountryDetector.is_us_zip(row["zip"]):
            return True
        elif row["state"] and CountryDetector.is_us_state(row["state"]):
            return True
        elif row["phone"] and CountryDetector.is_us_phone(row["phone"]):
            return True
        return False

    @staticmethod
    def is_canada(row):
        country = CountryDetector.fix_country(row["country_code"])
        if country == "ca":
            return True
        elif not ValidatorUtils.is_blank(country):
            return False
        elif row["zip"] and CountryDetector.is_canada_zip(row["zip"]):
            return True
        elif row["state"] and CountryDetector.is_canada_state(row["state"]):
            return True
        elif row["phone"] and CountryDetector.is_canada_phone(row["phone"]):
            return True
        return False
