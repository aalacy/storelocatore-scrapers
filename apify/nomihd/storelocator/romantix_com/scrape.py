# -*- coding: utf-8 -*-
import csv
from sgrequests import SgRequests
from sglogging import sglog
import json
import us

website = "romantix.com"
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

    search_url = "https://storemapper-herokuapp-com.global.ssl.fastly.net/api/users/6710/stores.js"
    stores_req = session.get(search_url, headers=headers)
    stores = json.loads(stores_req.text)["stores"]

    for store in stores:
        page_url = store["url"]
        if page_url == "":
            page_url = "<MISSING>"

        locator_domain = website
        location_name = store["name"]
        if location_name == "":
            location_name = "<MISSING>"

        address = store["address"]
        street_address = address.split(",")[0].strip()
        city = address.split(",")[1].strip()
        state = address.split(",")[-1].strip().split(" ")[0].strip()
        zip = address.split(",")[-1].strip().split(" ")[1].strip()

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
        if "#" in location_name:
            store_number = location_name.split("#")[1].strip()

        phone = store["phone"]

        location_type = "<MISSING>"
        hours = store["custom_field_1"]
        temp_hours = None
        if " / " in hours:
            temp_hours = hours.split("/")

        elif "<br>" in hours:
            temp_hours = hours.split("<br>")

        if temp_hours is not None:
            hours_list = []
            for hour in temp_hours:
                if len("".join(hour).strip()) > 0:
                    hours_list.append("".join(hour).strip())

            hours_of_operation = ";".join(hours_list).strip()
        else:
            hours_of_operation = hours

        latitude = store["latitude"]
        longitude = store["longitude"]

        if latitude == "" or latitude is None:
            latitude = "<MISSING>"
        if longitude == "" or longitude is None:
            longitude = "<MISSING>"

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

        # break
    return loc_list


def scrape():
    log.info("Started")
    data = fetch_data()
    write_output(data)
    log.info("Finished")


if __name__ == "__main__":
    scrape()
