import sys
import os
from glob import glob
import json
import phonenumbers
import us
import zipcodes
import re
import csv
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('emoryhealthcare_org')



#### Utilities

def touch(path):
    with open(path, 'a'):
        os.utime(path, None)

def fail(message):
    if debug:
        logger.info(message)
    else:
        raise AssertionError(message)

def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False

def is_valid_phone_number(phone, country):
    try:
        return phonenumbers.is_possible_number(phonenumbers.parse(phone, country))
    except:
        return False

def is_blank(field):
    if field in ['<MISSING>', '<INACCESSIBLE>']:
        return True
    return not bool(field)

#### Country detection

def fix_country(raw_country):
    if is_blank(raw_country):
        return None
    normalized = raw_country.strip().lower()
    if normalized in ["us", "usa", "united states", "united states of america"]:
        return "us"
    elif normalized in ["ca", "can", "canada"]:
        return "ca"
    else:
        return normalized

def is_us_zip(zip_code):
    cleaned_zip = str(zip_code).strip()
    try:
        return bool(zipcodes.matching(cleaned_zip))
    except:
        return False

def is_canada_zip(zip_code):
    pattern = re.compile("^[ABCEGHJ-NPRSTVXY][0-9][ABCEGHJ-NPRSTV-Z] [0-9][ABCEGHJ-NPRSTV-Z][0-9]$")
    return zip_code and pattern.match(zip_code)

def is_us_state(state):
    return bool(us.states.lookup(state))

def is_canada_state(state):
    return not is_blank(state) and state.strip().lower() in ['ab', 'alberta', 'bc', 'british columbia', 'mb', 'manitoba', 'nb', 'new brunswick', 'nl', 'newfoundland and labrador', 'nt', 'northwest territories', 'ns', 'nova scotia', 'nu', 'nunavut', 'on', 'ontario', 'pe', 'prince edward island', 'qc', 'quebec', 'sk', 'saskatchewan', 'yt', 'yukon']

def is_us_phone(phone):
    try:
        return phonenumbers.is_valid_number(phonenumbers.parse(phone, "US"))
    except:
        return False

def is_canada_phone(phone):
    try:
        return phonenumbers.is_valid_number(phonenumbers.parse(phone, "CA"))
    except:
        return False

def is_us(row):
    country = fix_country(row["country_code"])
    if country == "us":
        return True
    elif not is_blank(country):
        return False
    elif row["zip"] and is_us_zip(row["zip"]):
        return True
    elif row["state"] and is_us_state(row["state"]):
        return True
    elif row["phone"] and is_us_phone(row["phone"]):
        return True
    return False

def is_canada(row):
    country = fix_country(row["country_code"])
    if country == "ca":
        return True
    elif not is_blank(country):
        return False
    elif row["zip"] and is_canada_zip(row["zip"]):
        return True
    elif row["state"] and is_canada_state(row["state"]):
        return True
    elif row["phone"] and is_canada_phone(row["phone"]):
        return True
    return False

#### Country-Specific Checks

def check_us_state(row):
    state = row["state"]
    if not is_blank(state) and not us.states.lookup(state.strip()):
        fail("invalid state: {}".format(state))

def check_us_zip(row):
    zip_code = row["zip"]
    if is_blank(zip_code):
        return
    try:
        zipcodes.matching(str(zip_code))
    except:
        fail("invalid zip code: {}".format(zip_code)) 

def check_us_phone(row):
    phone = row["phone"]
    if not is_blank(phone) and not is_valid_phone_number(phone, "US"):
        fail("invalid phone number: {}".format(phone))

def check_canada_state(row):
    state = row["state"]
    if not is_blank(state) and not is_canada_state(state):
        fail("invalid Canadian province/territory: {}".format(state))

def check_canada_phone(row):
    phone = row["phone"]
    if not is_blank(phone) and not is_valid_phone_number(phone, "CA"):
        fail("invalid Canadian phone number: {}".format(phone))

def check_canada_zip(row):
    zip_code = row["zip"]
    if not is_blank(zip_code) and not is_canada_zip(zip_code):
        fail("invalid Canadian postal code: {}".format(zip_code))

#### General Checks

def check_latitude_and_longitude(row):
    latitude = row["latitude"]
    longitude = row["longitude"]
    if is_blank(latitude) and is_blank(longitude): 
        return
    if not is_blank(latitude) and is_blank(longitude):
        fail("latitude without corresponding longitude for row {}".format(row))
    if not is_blank(longitude) and is_blank(latitude):
        fail("longitude without corresponding latitude for row {}".format(row))
    if not is_number(latitude):
        fail("non-numeric latitude: {}".format(latitude))
    elif not (-90.0 <= float(latitude) <= 90.0):
        fail("latitude out of range: {}".format(latitude))
    if not is_number(longitude):
        fail("non-numeric longitude: {}".format(longitude))
    elif not (-180.0 <= float(longitude) <= 180.0):
        fail("longitude out of range: {}".format(longitude))

def check_schema(data):
    logger.info("validating output schama")
    required_columns = ["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"]
    for row in data:
        for column in row:
            if type(row[column]) not in [type(None), type(''), type(u''), type(0), type(0.0), type(True)]:
                fail("row {} contains unexpected data type {}".format(row, type(row[column])))
        for column in required_columns:
            if column not in row:
                fail("row {} does not contain required column {}".format(row, column))
    if not debug: logger.info("output schema looks good")

def check_duplication(data):
    logger.info("checking for duplicate rows in the data")
    keys = {}
    for row in data:
        key = (row["street_address"], row["city"], row["state"], row["zip"], row["country_code"], row["location_type"])
        if key in keys:
            fail("found duplicate key {} in the data".format(key))
    if not debug: logger.info("no duplicates found")

def check_values(data):
    logger.info("checking for data quality issues")
    for row in data:
        check_latitude_and_longitude(row)
        if is_us(row):
            check_us_state(row)
            check_us_zip(row)
            check_us_phone(row)
        elif is_canada(row):
            check_canada_state(row)
            check_canada_zip(row)
            check_canada_phone(row)
    if not debug: logger.info("no data quality issues found")

#### Entry Point

def validate(data):
    check_schema(data)
    check_values(data)
    check_duplication(data)

data = []
data_location = sys.argv[1]
debug = len(sys.argv) > 2 and sys.argv[2] == "DEBUG"

if data_location.endswith(".csv"):
    with open(data_location) as csv_file:
        reader = csv.DictReader(csv_file, skipinitialspace=True)
        for row in reader:
            data.append(row)
else:
    for f_name in glob(os.path.join(data_location, 'datasets/default', '*.json')):
        with open(f_name) as json_file:
            data.append(json.load(json_file))

validate(data)
if not debug:
    touch('./SUCCESS')

