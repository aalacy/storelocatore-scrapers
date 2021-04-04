# -*- coding: utf-8 -*-
import csv
from sgrequests import SgRequests
from sglogging import sglog
import json
import us

website = "salata.com"
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

    search_url = "https://order-api.salata.com/cms?collection=locations"
    stores_req = session.get(search_url, headers=headers)
    stores = json.loads(stores_req.text)
    for store in stores:
        page_url = "<MISSING>"
        locator_domain = website
        location_name = store["location_name"]
        if location_name == "":
            location_name = "<MISSING>"

        street_address = store["location_address_line_1"]
        city_state_zip = store["location_address_line_2"]
        city = ""
        state = ""
        zip = ""
        if "," in city_state_zip:
            city = city_state_zip.split(",")[0].strip()
            state = city_state_zip.split(",")[1].strip().split(" ")[0].strip()
            zip = city_state_zip.split(",")[1].strip().split(" ")[1].strip()
        else:
            restaurants = json.loads(
                session.get(
                    "https://order-api.salata.com/api/restaurants?includePrivate=true",
                    headers=headers,
                ).text
            )["restaurants"]
            for restaurant in restaurants:
                if store["olo_id"] == restaurant["id"]:
                    city = restaurant["city"]
                    state = restaurant["state"]
                    zip = restaurant["zip"]
                    break

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

        store_number = str(store["olo_id"])
        phone = store["telephone"]

        location_type = "<MISSING>"
        if store["temporarily_closed"] is True:
            location_type = "temporarily_closed"

        latitude = store["latitude"]
        longitude = store["longitude"]

        if latitude == "" or latitude is None:
            latitude = "<MISSING>"
        if longitude == "" or longitude is None:
            longitude = "<MISSING>"

        if phone == "" or phone is None:
            phone = "<MISSING>"

        hours_of_operation = (
            " ".join(store["hours_of_operation"].split("\n"))
            .strip()
            .replace("Temporary Hours: ", "")
            .strip()
            .replace("Temporarily Closed", "")
            .strip()
        )

        if "Permanently Closed" in hours_of_operation:
            location_type = "Permanently Closed"
            hours_of_operation = ""

        if hours_of_operation == "" or hours_of_operation is None:
            hours_of_operation = "<MISSING>"

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
