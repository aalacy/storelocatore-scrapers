from .validatorutils import ValidatorUtils


class CoordinatesChecker:
    def __init__(self, debug):
        self.debug = debug

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
