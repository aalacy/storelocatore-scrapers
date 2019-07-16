from .countrychecker import *


def check_latitude_and_longitude(row, debug):
    latitude = row["latitude"]
    longitude = row["longitude"]
    if is_blank(latitude) and is_blank(longitude):
        return
    if not is_blank(latitude) and is_blank(longitude):
        fail("latitude without corresponding longitude for row {}".format(row), debug)
    if not is_blank(longitude) and is_blank(latitude):
        fail("longitude without corresponding latitude for row {}".format(row), debug)
    if not is_number(latitude):
        fail("non-numeric latitude: {}".format(latitude), debug)
    elif not (-90.0 <= float(latitude) <= 90.0):
        fail("latitude out of range: {}".format(latitude), debug)
    if not is_number(longitude):
        fail("non-numeric longitude: {}".format(longitude), debug)
    elif not (-180.0 <= float(longitude) <= 180.0):
        fail("longitude out of range: {}".format(longitude), debug)


def check_schema(data, debug):
    print("validating output schama")
    required_columns = ["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"]
    for row in data:
        for column in row:
            if type(row[column]) not in [type(None), type(''), type(u''), type(0), type(0.0), type(True)]:
                fail("row {} contains unexpected data type {}".format(row, type(row[column])), debug)
        for column in required_columns:
            if column not in row:
                fail("row {} does not contain required column {}".format(row, column), debug)
    if not debug: print("output schema looks good")


def check_duplication(data, debug):
    print("checking for duplicate rows in the data")
    keys = {}
    for row in data:
        key = (row["street_address"], row["city"], row["state"], row["zip"], row["country_code"], row["location_type"])
        if key in keys:
            fail("found duplicate key {} in the data".format(key), debug)
    if not debug: print("no duplicates found")


def check_values(data, debug):
    print("checking for data quality issues")
    for row in data:
        check_latitude_and_longitude(row, debug)
        if is_us(row):
            check_us_state(row, debug)
            check_us_zip(row, debug)
            check_us_phone(row, debug)
        elif is_canada(row):
            check_canada_state(row, debug)
            check_canada_zip(row, debug)
            check_canada_phone(row, debug)
    if not debug: print("no data quality issues found")
