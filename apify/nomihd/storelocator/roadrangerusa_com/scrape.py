# -*- coding: utf-8 -*-
import csv
from sgrequests import SgRequests
from sglogging import sglog
import lxml.html
import us

website = "roadrangerusa.com"
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

    search_url = "https://www.roadrangerusa.com/locations-amenities/find-a-road-ranger"
    stores_req = session.get(search_url, headers=headers)
    stores_sel = lxml.html.fromstring(stores_req.text)
    stores = stores_sel.xpath('//li[@class="store-location-row"]')
    for store in stores:
        page_url = search_url

        locator_domain = website
        location_name = "".join(
            store.xpath('.//h4[@class="store-location-teaser__address"]/text()')
        ).strip()
        if location_name == "":
            location_name = "<MISSING>"

        address = "".join(location_name).split("(")[0]
        if len(address.split(",")) == 3:
            street_address = address.split(",")[0].strip()
            city = address.split(",")[1].strip()
            state = address.split(",")[2].strip()
        elif len(address.split(",")) == 2:
            street_address = address.split(",")[0].strip()
            city = " ".join(address.split(",")[1].strip().rsplit(" ", 1)[:-1]).strip()
            state = address.split(",")[1].strip().rsplit(" ", 1)[-1].strip()

        zip = "<MISSING>"
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
        phone = "".join(store.xpath('.//a[contains(@href,"tel:")]/text()')).strip()
        location_type = "<MISSING>"
        hours_of_operation = "<MISSING>"
        latitude = (
            "".join(store.xpath('.//span[@class="coordinates"]/text()'))
            .strip()
            .replace("Coordinates:", "")
            .strip()
            .split(",")[0]
            .strip()
        )
        longitude = (
            "".join(store.xpath('.//span[@class="coordinates"]/text()'))
            .strip()
            .replace("Coordinates:", "")
            .strip()
            .split(",")[1]
            .strip()
        )

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
