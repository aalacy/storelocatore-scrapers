import re
import us
import zipcodes
from .validatorutils import *

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