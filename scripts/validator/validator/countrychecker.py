from .countrydetection import *

def check_us_state(row, debug):
    state = row["state"]
    if not is_blank(state) and not us.states.lookup(state.strip()):
        fail("invalid state: {}".format(state), debug)

def check_us_zip(row, debug):
    zip_code = row["zip"]
    try:
        if not is_blank(zip_code) and not zipcodes.matching(str(zip_code)):
            fail("invalid zip code: {}".format(zip_code), debug)
    except:
        fail("invalid zip code: {}".format(zip_code), debug)

def check_us_phone(row, debug):
    phone = row["phone"]
    if not is_blank(phone) and not is_valid_phone_number(phone, "US"):
        fail("invalid phone number: {}".format(phone), debug)

def check_canada_state(row, debug):
    state = row["state"]
    if not is_blank(state) and not is_canada_state(state):
        fail("invalid Canadian province/territory: {}".format(state), debug)

def check_canada_phone(row, debug):
    phone = row["phone"]
    if not is_blank(phone) and not is_valid_phone_number(phone, "CA"):
        fail("invalid Canadian phone number: {}".format(phone), debug)

def check_canada_zip(row, debug):
    zip_code = row["zip"]
    if not is_blank(zip_code) and not is_canada_zip(zip_code):
        fail("invalid Canadian postal code: {}".format(zip_code), debug)