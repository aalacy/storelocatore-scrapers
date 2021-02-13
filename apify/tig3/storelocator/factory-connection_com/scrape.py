import csv
from sglogging import sglog
import subprocess
import json
from Naked.toolshed.shell import muterun_js  # noqa
from sgscrape import sgpostal as parser
import re

LOCATOR_DOMAIN = "www.factory-connection.com"
PAGE_URL = "https://app.locatedmap.com/initwidget/?instanceId=fb5794db-1003-4eb9-8d61-3912f1b0e26a&compId=comp-k2z7snsm&viewMode=site&styleId=style-k2z7svc0"
log = sglog.SgLogSetup().get_logger(logger_name=LOCATOR_DOMAIN, stdout_log_level="INFO")


def write_output(data):
    with open("data.csv", mode="w", newline="", encoding="utf8") as output_file:
        writer = csv.writer(
            output_file, delimiter=",", quotechar='"', quoting=csv.QUOTE_ALL
        )

        # Header
        writer.writerow(
            [
                "locator_domain",
                "page_url",
                "location_name",
                "street_address",
                "city",
                "state",
                "zip",
                "country_code",
                "store_number",
                "phone",
                "location_type",
                "latitude",
                "longitude",
                "hours_of_operation",
            ]
        )

        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    npm_install()

    log.info("Calling get_data.js")
    response = muterun_js("get_data.js")

    if response.exitcode == 0:
        json_string = response.stdout
    else:
        log.error("Error in get_data.js file")
        log.error(response.stderr)
        exit("EXITING...")

    data = []
    jsn = json.loads(json_string)

    log.info("Processing data")
    for row in jsn:
        location_name = check_missing(row["name"])
        formatted_address = row["formatted_address"]

        addrs = parser.parse_address_usa(formatted_address)
        street_address = check_missing(addrs.street_address_1)
        street_address = (
            (street_address + ", " + addrs.street_address_2)
            if addrs.street_address_2
            else street_address
        )
        location_type = check_missing()

        city = addrs.city
        state = addrs.state
        zip = addrs.postcode
        country_code = addrs.country

        store_number = check_missing()
        phone = row["tel"]
        if not phone and row["formatted_tel"]:
            phone = row["formatted_tel"]

        phone = check_missing(phone)
        latitude = check_missing(row["latitude"])
        longitude = check_missing(row["longitude"])
        hours_of_operation = get_hours_of_operation(row["opening_hours"]).replace(
            "\n", "; "
        )

        data.append(
            [
                LOCATOR_DOMAIN,
                PAGE_URL,
                location_name,
                street_address,
                city,
                state,
                zip,
                country_code,
                store_number,
                phone,
                location_type,
                latitude,
                longitude,
                hours_of_operation,
            ]
        )

    return data


# For cases when there is no city
def get_missing_city(formatted_address):
    lst1 = formatted_address.split(",")
    return lst1[0].split(" ")[-1]


# missing or invalid/too short street address
def parse_missing_street_address(raw_street_address):
    rgx = re.compile(r"^[a-zA-Z\s]+")
    res = rgx.findall(raw_street_address)

    building_name = ""
    street_address = ""
    if res:
        building_name = res[0].strip()
        street_address = raw_street_address.replace(building_name, "", 1).strip()

    return building_name, street_address


def npm_install():
    log.info("Custom npm install")
    subprocess.call("npm install axios", shell=True)
    subprocess.call("npm install atob", shell=True)
    subprocess.call("npm install pako", shell=True)


def get_hours_of_operation(hours):
    hours = check_missing(hours)

    if "Hours:" in hours:
        lst = hours.split("Hours:")
        return lst[1].strip()

    return hours


# to be moved to general class
# If empty string - returns "<MISSING>" keyword
def check_missing(val=""):
    if not val:
        return "<MISSING>"
    else:
        return val


# to be moved to general class
# If empty string - returns "<INACCESSIBLE>" keyword
def check_inaccessible(val=""):
    if not val:
        return "<INACCESSIBLE>"
    else:
        return val


def scrape():
    log.info("Start...")
    data = fetch_data()
    log.info("Data fetched. Writing output...")
    write_output(data)
    log.info("Finished")


if __name__ == "__main__":
    scrape()
