# -*- coding: utf-8 -*-
import csv
from sgrequests import SgRequests
from sglogging import sglog
import json
import lxml.html

website = "puregym.com"
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

    search_url = "https://www.puregym.com/gyms/"

    stores_req = session.get(search_url, headers=headers)
    json_text = (
        stores_req.text.split(
            "ReactDOM.render(React.createElement(Search.default.GymSearchListRoot,"
        )[1]
        .strip()
        .split("}}),")[0]
        .strip()
        + "}}"
    )
    stores = json.loads(json_text)["allGyms"]

    for store in stores:
        latitude = store["latitude"]
        longitude = store["longitude"]
        page_url = "https://www.puregym.com" + store["url"]

        locator_domain = website
        location_name = store["name"]
        if location_name == "":
            location_name = "<MISSING>"

        log.info(page_url)
        store_req = session.get(page_url, headers=headers)
        store_sel = lxml.html.fromstring(store_req.text)
        store_json = json.loads(
            "".join(
                store_sel.xpath('//script[@type="application/ld+json"]/text()')
            ).strip()
        )

        street_address = store["address1"]
        if "address2" in store:
            if store["address2"] is not None and len(store["address2"]) > 0:
                street_address = street_address + ", " + store["address2"]

        city = store_json["location"]["address"]["addressLocality"]
        state = "<MISSING>"
        zip = store_json["location"]["address"]["postalCode"]
        country_code = "GB"
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

        store_number = str(store["id"])
        location_type = "<MISSING>"
        if store["status"] == 3:
            location_type = "temp_closed"
        if store["status"] == 4:
            location_type = "opening_soon"
        if store["status"] == 1:
            location_type = "coming_soon"

        phone = store_json["telephone"]
        hours_of_operation = "; ".join(
            store_sel.xpath('//div[@class="gym-hours"]/table//tr//text()')
        ).strip()

        if latitude == "" or latitude is None:
            latitude = "<MISSING>"
        if longitude == "" or longitude is None:
            longitude = "<MISSING>"

        if hours_of_operation == "" or hours_of_operation is None:
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
