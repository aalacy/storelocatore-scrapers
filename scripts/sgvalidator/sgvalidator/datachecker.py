from .validatorutils import *
from .fillratechecker import FillRateChecker
from .trashvaluechecker import TrashValueChecker
from .countrydetector import CountryDetector
from .countrychecker import CountryChecker


class DataChecker:
    def __init__(self, data, debug):
        self.data = data
        self.debug = debug

    def check_data(self):
        self.check_duplication()
        self.check_schema()
        self.check_country_specific_values()
        self.check_for_trash_values()
        self.check_for_fill_rate() # doesn't cause anything to fail, just prints warning messages

    def check_schema(self):
        print(termcolor.colored("Validating output schema...", "blue"))
        required_columns = ["locator_domain", "location_name", "street_address", "city", "state", "zip",
                            "country_code", "store_number", "phone", "location_type", "latitude", "longitude",
                            "hours_of_operation"]
        for row in self.data:
            for column in row:
                if type(row[column]) not in [type(None), type(''), type(u''), type(0), type(0.0), type(True)]:
                    ValidatorUtils.fail("row {} contains unexpected data type {}".format(row, type(row[column])), self.debug)
            for column in required_columns:
                if column not in row:
                    ValidatorUtils.fail("row {} does not contain required column {}".format(row, column), self.debug)
        if not self.debug: print(termcolor.colored("Output schema looks good!", "green"))

    def check_duplication(self):
        print(termcolor.colored("Checking for duplicate rows in the data...", "blue"))
        keys = set()
        for row in self.data:
            key = (row["street_address"], row["city"], row["state"], row["zip"], row["country_code"],
                   row["location_type"])
            if key in keys:
                ValidatorUtils.fail("Found duplicate key {} in the data".format(key), self.debug)
            else:
                keys.add(key)
        if not self.debug: print(termcolor.colored("No duplicates found...", "green"))

    def check_country_specific_values(self):
        country_checker = CountryChecker(self.debug)
        print(termcolor.colored("Checking for data quality issues...", "blue"))
        for row in self.data:
            self.check_latitude_and_longitude(row)
            if CountryDetector.is_us(row):
                country_checker.check_us_state(row)
                country_checker.check_us_zip(row)
                country_checker.check_us_phone(row)
            elif CountryDetector.is_canada(row):
                country_checker.check_canada_state(row)
                country_checker.check_canada_zip(row)
                country_checker.check_canada_phone(row)
        if not self.debug: print(termcolor.colored("No data quality issues found...", "green"))

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

    def check_for_trash_values(self):
        for row in self.data:
            res = TrashValueChecker.findTrashValues(row)
            if res is not None:
                ValidatorUtils.fail("Row {} contains trash value: {}".format(row, res), self.debug)

    def check_for_fill_rate(self):
        FillRateChecker.checkFillRate(self.data)

