# -*- coding: utf-8 -*-
import csv
from sgrequests import SgRequests
from sglogging import sglog
import lxml.html
import json

website = "ezpawn.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
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

    stores_req = session.get(
        "https://ezpawn.com/data/locations/ezpawn/output/locations.json",
        headers=headers,
    )
    stores = json.loads(stores_req.text)
    for store in stores:

        locator_domain = website
        location_name = store["name2"]
        street_address = store["address"]
        city = store["city"].replace(" ", "-").strip()
        state = store["state"]
        zip = store["zip"]
        country_code = store["countryCode"]
        store_number = "<MISSING>"
        phone = store["phone"]
        location_type = store["name"]

        if location_type == "":
            location_type = "<MISSING>"

        latitude = store["latitude"]
        longitude = store["longitude"]
        page_url = (
            "https://ezpawn.com/stores/"
            + state
            + "/"
            + city
            + "/"
            + street_address.replace(".", "").replace(" ", "-").strip()
        )
        log.info(page_url)
        store_req = session.get(page_url, headers=headers)
        store_sel = lxml.html.fromstring(store_req.text)
        days = store_sel.xpath('//dl[@class="sched-box"]/dt/text()')
        time = store_sel.xpath('//dl[@class="sched-box"]/dd/text()')
        hours_list = []
        for index in range(0, len(days)):
            hours_list.append(days[index] + ":" + time[index])

        hours_of_operation = "; ".join(hours_list).strip()

        if hours_of_operation == "":
            hours_of_operation = "<MISSING>"

        if street_address == "":
            street_address = "<MISSING>"

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

    return loc_list


def scrape():
    log.info("Started")
    data = fetch_data()
    write_output(data)
    log.info("Finished")


if __name__ == "__main__":
    scrape()
