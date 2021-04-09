# -*- coding: utf-8 -*-
import csv
from sgrequests import SgRequests
from sglogging import sglog
import lxml.html
import us

website = "studiomoviegrill.com"
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

    search_url = "https://www.studiomoviegrill.com/locations"
    stores_req = session.get(search_url, headers=headers)
    stores_sel = lxml.html.fromstring(stores_req.text)
    stores = stores_sel.xpath('//div[@class="location-box"]')
    for store in stores:
        page_url = (
            "https://studiomoviegrill.com" + "".join(store.xpath("h3/a/@href")).strip()
        )

        locator_domain = website
        location_name = "".join(store.xpath("h3/a/text()")).strip()
        if location_name == "":
            location_name = "<MISSING>"

        add_list = []
        address = store.xpath('p[@class="info"]/a[@target="_blank"]/text()')
        for add in address:
            if len("".join(add).strip()) > 0:
                add_list.append("".join(add).strip())

        street_address = add_list[0].strip()
        city = add_list[1].strip().split(",")[0].strip()
        state = add_list[1].strip().split(",")[1].strip().split(" ")[0].strip()
        zip = add_list[1].strip().split(",")[1].strip().split(" ")[-1].strip()

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
        phone = "".join(
            store.xpath('p[@class="info"]/a[contains(@href,"tel:")]/text()')
        ).strip()
        raw_text = store.xpath('p[@class="info"]/span[@class="caps"]/b/text()')
        location_type = "<MISSING>"
        if "RE-OPENING" not in ", ".join(raw_text).strip():
            if "OPENING" in ", ".join(raw_text).strip():
                location_type = "Coming Soon"
            if "TEMPORARILY CLOSED" in ", ".join(raw_text).strip():
                location_type = "TEMPORARILY CLOSED"

        hours_list = []
        for index in range(1, len(raw_text)):
            if "SPRING BRK" in raw_text[index]:
                continue
            else:
                hours_list.append(raw_text[index])

        hours_of_operation = "; ".join(hours_list).strip()
        if hours_of_operation == "":
            hours_of_operation = "<MISSING>"

        map_link = "".join(
            store.xpath('p[@class="info"]/a[@target="_blank"]/@href')
        ).strip()
        latitude = "<MISSING>"
        longitude = "<MISSING>"
        if len(map_link) > 0:
            latitude = map_link.split("!3d")[1].strip().split("!")[0].strip()
            longitude = map_link.split("!2d")[1].strip().split("!")[0].strip()

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
