import re
import csv
from io import BytesIO
from sglogging import sglog
from urllib.request import urlopen
from pdfreader import SimplePDFViewer
import usaddress

DOMAIN = "wagabag.com"
BASE_URL = "http://www.wagabag.com/store-locations/"
LOCATION_URL = "http://www.wagabag.com/wp-content/uploads/2015/07/Store-Locations-detail-02052019.pdf"
log = sglog.SgLogSetup().get_logger(logger_name=DOMAIN)


def write_output(data):
    with open("data.csv", mode="w") as output_file:
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


def handle_missing(field):
    if field is None or (isinstance(field, str) and len(field.strip()) == 0):
        return "<MISSING>"
    return field


def read_pdf(url):
    with urlopen(url) as file:
        mem_file = BytesIO(file.read())
        viewer = SimplePDFViewer(mem_file)
        return viewer


def parse_address(full_address):
    street_address = ""
    city = "<MISSING>"
    state = "<MISSING>"
    zip_code = "<MISSING>"
    if "Round Rock" in full_address:
        full_address = full_address.replace("Round Rock", "")
        city = "Round Rock"
    if "Liberty Hill" in full_address:
        full_address = full_address.replace("Liberty Hill", "")
        city = "Liberty Hill"
    if "Georgetown" in full_address:
        full_address = full_address.replace("Georgetown", "")
        city = "Georgetown"
    if "Hutto" in full_address:
        full_address = full_address.replace("Hutto", "")
        city = "Hutto"
    parsed_add = usaddress.tag(full_address)[0]
    if "AddressNumber" in parsed_add:
        street_address += parsed_add["AddressNumber"] + " "
    if "StreetNamePreDirectional" in parsed_add:
        street_address += parsed_add["StreetNamePreDirectional"] + " "
    if "StreetNamePreType" in parsed_add:
        street_address += parsed_add["StreetNamePreType"] + " "
    if "StreetName" in parsed_add:
        street_address += parsed_add["StreetName"] + " "
    if "StreetNamePostType" in parsed_add:
        street_address += parsed_add["StreetNamePostType"] + " "
    if "OccupancyType" in parsed_add:
        street_address += parsed_add["OccupancyType"] + " "
    if "OccupancyIdentifier" in parsed_add:
        street_address += parsed_add["OccupancyIdentifier"] + " "

    street_address = street_address.strip()
    if (
        "PlaceName" in parsed_add
        and "Round Rock" not in full_address
        and "Liberty Hill" not in full_address
        and "Georgetown" not in full_address
        and "Hutto" not in full_address
    ):
        city = parsed_add["PlaceName"].strip()
    if "StateName" in parsed_add:
        state = parsed_add["StateName"].strip()
    if "ZipCode" in parsed_add:
        zip_code = parsed_add["ZipCode"].strip()

    return street_address, city, state, zip_code


def read_pdf_to_dataframes(url):
    store_info = []
    viewer = read_pdf(url)
    for canvas in viewer:
        content = "".join(canvas.strings)
        regex = re.compile(r"(?=store\s#\d+)", re.IGNORECASE)
        store_data = regex.split(content)
        store_name_regex = r"(Store\s#(\d+))"
        location_type_regex = r"(Shell|Valero|No Fuel)"
        address_regex = r"(.*)"
        phone_regex = r"(\d{3}-\d{3}-\d{4})"
        regex = re.compile(
            fr"{store_name_regex}\s+{location_type_regex}\s+{address_regex}\s+{phone_regex}",
            re.IGNORECASE,
        )
        for store in store_data:
            if not store.strip():
                continue
            search = regex.search(store)
            location_name = search.group(1)
            store_number = search.group(2)
            location_type = search.group(3)
            address = search.group(4)
            phone = search.group(5)
            store_info.append(
                {
                    "location_name": location_name,
                    "store_number": store_number,
                    "location_type": location_type,
                    "address": address,
                    "phone": phone,
                }
            )

    return store_info


def fetch_data():
    locations = []
    store_info = read_pdf_to_dataframes(LOCATION_URL)
    for row in store_info:
        location_name = row["location_name"]
        address = row["address"]
        if "Pflugerville" in row["address"]:
            address = re.sub(r"\d{2,3}\-\d{2,3}\-\d{2,3}.*", "", row["address"])
        street_address, city, state, zip_code = parse_address(address)
        country_code = "US"
        phone = row["phone"]
        store_number = row["store_number"]
        latitude = "<MISSING>"
        longitude = "<MISSING>"
        location_type = row["location_type"]
        hours_of_operation = "<MISSING>"
        log.info("Append {} => {}".format(location_name, street_address))
        locations.append(
            [
                DOMAIN,
                BASE_URL,
                location_name,
                street_address,
                city,
                state,
                zip_code,
                country_code,
                store_number,
                phone,
                location_type,
                latitude,
                longitude,
                hours_of_operation,
            ]
        )
    return locations


def scrape():
    log.info("Start {} Scraper".format(DOMAIN))
    data = fetch_data()
    log.info("Found {} locations".format(len(data)))
    write_output(data)
    log.info("Finish processed " + str(len(data)))


scrape()
