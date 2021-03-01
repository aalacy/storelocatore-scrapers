import csv
from sgrequests import SgRequests
import json
from sglogging import SgLogSetup
from sgscrape import sgpostal as parser

logger = SgLogSetup().get_logger("gianteagle_com")


session = SgRequests()


def write_output(data):
    with open("data.csv", mode="w", newline="", encoding="utf-8") as output_file:
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
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "Accept": "*/*",
    }

    base_url = "https://www.gianteagle.com"

    # it will used in store data.
    locator_domain = base_url
    page_url = "<MISSING>"
    location_name = ""
    street_address = ""
    city = ""
    state = ""
    zipp = ""
    country_code = "US"
    store_number = ""
    phone = ""
    location_type = ""
    latitude = ""
    longitude = ""
    hours_of_operation = ""

    isFinish = False
    skip_counter = 0
    while isFinish is False:
        r_locations = session.get(
            "https://www.gianteagle.com/api/sitecore/locations/getlocations?q=&skip="
            + str(skip_counter),
            headers=headers,
        )
        json_locations = json.loads(r_locations.text)

        if len(json_locations) <= 0:
            logger.info("No more locations")
            break
        logger.info(
            str(skip_counter) + " json_locations == " + str(len(json_locations))
        )
        skip_counter += len(json_locations)

        for location_super_market in json_locations:
            store_number = location_super_market["Id"]
            location_name = location_super_market["Name"]
            raw_address = location_super_market["Address"]["lineOne"]
            if (
                location_super_market["Address"]["lineTwo"] is not None
                and location_super_market["Address"]["lineTwo"].strip() != "-"
            ):
                raw_address += ", " + location_super_market["Address"]["lineTwo"]

            formatted_addr = parser.parse_address_usa(raw_address)
            street_address = formatted_addr.street_address_1
            if formatted_addr.street_address_2:
                street_address = street_address + ", " + formatted_addr.street_address_2

            city = location_super_market["Address"]["City"]
            state = location_super_market["Address"]["State"]["Abbreviation"]
            zipp = location_super_market["Address"]["Zip"]
            phone = location_super_market["TelephoneNumbers"][0]["DisplayNumber"]
            latitude = str(location_super_market["Address"]["Coordinates"]["Latitude"])
            longitude = str(
                location_super_market["Address"]["Coordinates"]["Longitude"]
            )
            location_type = location_super_market["Details"]["Type"]["Name"]

            hours_of_operation = ""
            index = 0
            days = [
                "Sunday",
                "Monday",
                "Tuesday",
                "Wednesday",
                "Thursday",
                "Friday",
                "Saturday",
            ]
            for time_period in location_super_market["HoursOfOperation"]:
                if time_period["DayNumber"] == index + 1:
                    hours_of_operation += (
                        days[index] + " " + time_period["HourDisplay"] + " "
                    )
                index += 1

            store = [
                locator_domain,
                page_url,
                location_name,
                street_address,
                city,
                state,
                zipp,
                country_code,
                store_number,
                phone,
                location_type,
                latitude,
                longitude,
                hours_of_operation,
            ]

            store = [x.strip() if x and x else "<MISSING>" for x in store]

            yield store


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
