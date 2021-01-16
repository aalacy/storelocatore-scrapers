# -*- coding: utf-8 -*-
import csv
from sgrequests import SgRequests
from sglogging import sglog
import json
import lxml.html

website = "leeannchin.com"
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

    search_url = "https://www.leeannchin.com/locations"
    stores_req = session.get(search_url, headers=headers)
    json_text = (
        stores_req.text.split("var jsonContent = ")[1].strip().split("]};")[0].strip()
        + "]}"
    )
    stores = json.loads(json_text)["data"]

    for store in stores:
        page_url = store["url"]

        locator_domain = website
        location_name = store["title"]
        if location_name == "":
            location_name = "<MISSING>"

        street_address = store["street_number"].strip() + " " + store["address_route"]

        if len(store["subpremise"]) > 0:
            street_address = street_address + " " + store["subpremise"]
        city = store["city"].strip()
        state = store["state"].strip()
        zip = store["postal_code"].strip()
        country_code = store["country"].strip()

        if country_code == "":
            country_code = "<MISSING>"

        if street_address == "" or street_address is None:
            street_address = "<MISSING>"

        if city == "" or city is None:
            city = "<MISSING>"

        if state == "" or state is None:
            state = "<MISSING>"

        if zip == "" or zip is None:
            zip = "<MISSING>"

        if country_code == "" or country_code is None:
            country_code = "<MISSING>"

        store_number = store["id"]
        phone = store["phone"].strip()

        location_type = "<MISSING>"

        latitude = store["lat"]
        longitude = store["lng"]

        if latitude == "" or latitude is None:
            latitude = "<MISSING>"
        if longitude == "" or longitude is None:
            longitude = "<MISSING>"

        hours_of_operation = ""
        hours_sel = lxml.html.fromstring(store["hours"])
        hours = hours_sel.xpath("//li")
        hours_list = []
        for hour in hours:
            hours_list.append("".join(hour.xpath("text()")).strip())

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
