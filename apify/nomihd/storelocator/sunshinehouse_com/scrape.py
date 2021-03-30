# -*- coding: utf-8 -*-
import csv
from sgrequests import SgRequests
from sglogging import sglog
import json
import us
import lxml.html

website = "sunshinehouse.com"
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

    search_url = "https://sunshinehouse.com/find-a-location/"
    stores_req = session.get(search_url, headers=headers)
    stores_sel = lxml.html.fromstring(stores_req.text)
    stores = json.loads(
        "".join(stores_sel.xpath('//div[@id="g_map"]/@data-markers'))
        .strip()
        .replace("&quot;", '"')
        .strip()
    )
    for store in stores:
        page_url = "https://sunshinehouse.com" + store["Url"]
        locator_domain = website
        location_name = store["Title"]
        if location_name == "":
            location_name = "<MISSING>"

        street_address = store["Street1"]
        city = store["City"]
        state = store["State"]
        zip = store["PostalCode"]

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

        store_number = str(store["Id"])
        phone = store["PhoneNumber"]

        location_type = "<MISSING>"

        latitude = store["Latitude"]
        longitude = store["Longitude"]

        if latitude == "":
            latitude = "<MISSING>"
        if longitude == "":
            longitude = "<MISSING>"

        if phone == "":
            phone = "<MISSING>"

        store_req = session.get(page_url, headers=headers)
        store_sel = lxml.html.fromstring(store_req.text)

        details = store_sel.xpath('//p[@class="center-details"]')
        hours_of_operation = ""
        for det in details:
            if "fas fa-clock" in "".join(det.xpath("i/@class")).strip():
                hours_of_operation = "".join(det.xpath("text()")).strip()

        if hours_of_operation == "":
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
