# -*- coding: utf-8 -*-
import csv
from sgrequests import SgRequests
from sglogging import sglog
import json
import us
import usaddress

website = "shoneys.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36",
    "Accept": "application/json",
}


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
        temp_list = []  # ignoring duplicates
        for row in data:
            comp_list = [
                row[2].strip(),
                row[3].strip(),
                row[4].strip(),
                row[5].strip(),
                row[6].strip(),
                row[8].strip(),
                row[10].strip(),
            ]
            if comp_list not in temp_list:
                temp_list.append(comp_list)
                writer.writerow(row)

        log.info(f"No of records being processed: {len(temp_list)}")


def fetch_data():
    # Your scraper here
    loc_list = []

    search_url = "https://www.shoneys.com/wp-json/wp/v2/locations"
    stores_req = session.get(search_url, headers=headers)
    stores = json.loads(stores_req.text)
    for store in stores:
        page_url = "<MISSING>"
        locator_domain = website
        location_name = (
            store["title"]["rendered"]
            .encode("ascii", "replace")
            .decode("utf-8")
            .replace("?", "'")
            .strip()
            .replace("&#8217;", "'")
            .strip()
        )
        if location_name == "":
            location_name = "<MISSING>"

        address = store["acf"]["address"]["address"]
        street_address = address.split(",")[0].strip()
        city = ""
        state = ""
        zip = ""
        parsed_address = usaddress.parse(address)
        for index, tuple in enumerate(parsed_address):
            if tuple[1] == "PlaceName":
                city = city + tuple[0].strip() + " "
            if tuple[1] == "StateName":
                if len(state) <= 0:
                    state = tuple[0].replace(",", "").strip()
            if tuple[1] == "ZipCode":
                zip = tuple[0].replace(",", "").strip()

        city = city.replace(",", "").strip()
        country_code = "<MISSING>"
        if us.states.lookup(state):
            country_code = "US"

        if street_address == "":
            street_address = "<MISSING>"

        if city == "":
            city = "<MISSING>"

        if state == "":
            state = "<MISSING>"

        if zip == "":
            zip = "<MISSING>"

        store_number = "<MISSING>"
        phone = store["acf"]["phone"]

        location_type = store["acf"]["status"]
        hours = store["acf"]["working_hours"]
        hours_of_operation = ""
        for day, time in hours.items():
            hours_of_operation = hours_of_operation + day + ":" + time + " "

        hours_of_operation = hours_of_operation.strip()

        latitude = store["acf"]["address"]["lat"]
        longitude = store["acf"]["address"]["lng"]

        if latitude == "":
            latitude = "<MISSING>"
        if longitude == "":
            longitude = "<MISSING>"

        if hours_of_operation == "":
            hours_of_operation = "<MISSING>"
        if phone == "":
            phone = "<MISSING>"

        curr_list = [
            locator_domain,
            page_url,
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
        loc_list.append(curr_list)

        # break
    return loc_list


def scrape():
    log.info("Started")
    data = fetch_data()
    write_output(data)
    log.info("Finished")


if __name__ == "__main__":
    scrape()
