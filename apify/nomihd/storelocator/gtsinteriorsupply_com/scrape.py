# -*- coding: utf-8 -*-
import csv
from sgrequests import SgRequests
from sglogging import sglog
import json
import us

website = "gtsinteriorsupply.com"
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

    search_url = "https://gtsinteriorsupply.com/Contact.do"
    stores_req = session.get(search_url, headers=headers)
    json_text = (
        stores_req.text.split("required :items='")[1].strip().split("}]'")[0].strip()
        + "}]"
    )
    json_text = json_text.replace("&#34;", '"').strip()
    stores = json.loads(json_text)
    for store in stores:
        page_url = "https://gtsinteriorsupply.com/" + store["aboutUrl"]
        locator_domain = website
        location_name = store["name"]
        if location_name == "":
            location_name = "<MISSING>"

        street_address = store["address1"]
        if store["address2"] is not None:
            if len(store["address2"]) > 0:
                street_address = street_address + ", " + store["address2"]

        city = store["city"].strip()
        state = store["state"].strip()
        zip = store["postalCode"].strip()

        country_code = "<MISSING>"
        if us.states.lookup(state):
            country_code = "US"

        if street_address == "" or street_address is None:
            street_address = "<MISSING>"

        if city == "" or city is None:
            city = "<MISSING>"

        if state == "" or state is None:
            state = "<MISSING>"

        if zip == "" or zip is None:
            zip = "<MISSING>"

        store_number = "<MISSING>"
        phone = store["phone1"]

        location_type = "<MISSING>"
        latitude = store["latitude"]
        longitude = store["longitude"]

        if latitude == "" or latitude is None:
            latitude = "<MISSING>"
        if longitude == "" or longitude is None:
            longitude = "<MISSING>"

        hours_of_operation = ""
        hours_list = []
        if store["weekdayHours"] is not None:
            hours_list.append(
                store["weekdayHours"]
                .encode("ascii", "replace")
                .decode("utf-8")
                .replace("?", "-")
                .strip()
                .replace("Hours:", "")
                .strip()
            )

        if store["saturdayHours"] is not None:
            hours_list.append(
                store["saturdayHours"]
                .encode("ascii", "replace")
                .decode("utf-8")
                .replace("?", "-")
                .strip()
                .replace("Hours:", "")
                .strip()
            )

        hours_of_operation = "; ".join(hours_list).strip()

        if hours_of_operation == "":
            hours_of_operation = "<MISSING>"

        if phone == "" or phone is None:
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

    return loc_list


def scrape():
    log.info("Started")
    data = fetch_data()
    write_output(data)
    log.info("Finished")


if __name__ == "__main__":
    scrape()
