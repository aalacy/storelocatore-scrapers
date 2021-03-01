# -*- coding: utf-8 -*-
import csv
from sgrequests import SgRequests
from sglogging import sglog
import lxml.html
import us
import json

website = "choctawcasinos.com"
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

    search_url = "https://www.choctawcasinos.com/locations/"
    stores_req = session.get(search_url, headers=headers)
    stores_sel = lxml.html.fromstring(stores_req.text)
    stores = stores_sel.xpath('//div[@class="col-sm-4 casino-location-container"]')
    for store in stores:
        locator_domain = website
        page_url = "".join(store.xpath("h2/a/@href")).strip()
        log.info(page_url)
        store_req = session.get(page_url, headers=headers)
        store_sel = lxml.html.fromstring(store_req.text)

        latlng = "".join(
            store_sel.xpath(
                '//div[@class="directions-holder"]/div[@class="directions-map"]/@data-coords'
            )
        ).strip()
        latitude = latlng.split(",")[0].strip()
        longitude = latlng.split(",")[1].strip()
        store_json = json.loads(
            store_sel.xpath('//script[@type="application/ld+json"]/text()')[-1]
        )

        location_name = (
            store_json["name"]
            .replace("&amp;", "&")
            .encode("ascii", "replace")
            .decode("utf-8")
            .replace("?", "-")
            .strip()
        )
        if location_name == "":
            location_name = "<MISSING>"

        street_address = store_json["address"]["streetAddress"]
        city = store_json["address"]["addressLocality"]
        state = store_json["address"]["addressRegion"]
        zip = store_json["address"]["postalCode"]

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
        location_type = "<MISSING>"
        phone = store_json["telephone"]

        hours_of_operation = "".join(
            store_sel.xpath('//div[@class="directions-info"]/h5//text()')
        ).strip()

        if country_code == "" or country_code is None:
            country_code = "<MISSING>"

        if phone == "" or phone is None:
            phone = "<MISSING>"

        if latitude == "" or latitude is None:
            latitude = "<MISSING>"
        if longitude == "" or longitude is None:
            longitude = "<MISSING>"

        if hours_of_operation == "":
            hours_of_operation = "<MISSING>"

        if location_type == "":
            location_type = "<MISSING>"

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

    """ casinos too """

    stores = stores_sel.xpath('//div[@class="too-location"]')
    for store in stores:
        locator_domain = website
        page_url = "https://www.choctawcasinos.com/locations/"
        latitude = "<MISSING>"
        longitude = "<MISSING>"

        location_name = "".join(store.xpath("h3/text()")).strip()
        if location_name == "":
            location_name = "<MISSING>"

        address = store.xpath('h6[@class="address"]/span/a/text()')
        add_list = []
        for add in address:
            if len("".join(add)) > 0:
                add_list.append("".join(add))

        street_address = " ".join(add_list[:-1]).strip()
        city = add_list[-1].strip().split(",")[0].strip()
        state = add_list[-1].strip().split(",")[1].strip().split(" ")[0].strip()
        zip = add_list[-1].strip().split(",")[1].strip().split(" ")[-1].strip()

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
        location_type = "<MISSING>"
        phone = "".join(store.xpath('h6[@class="phone"]/span/a/text()')).strip()

        hours_of_operation = "".join(
            store.xpath('h6[@class="time"]/span/text()')
        ).strip()

        if country_code == "" or country_code is None:
            country_code = "<MISSING>"

        if phone == "" or phone is None:
            phone = "<MISSING>"

        if latitude == "" or latitude is None:
            latitude = "<MISSING>"
        if longitude == "" or longitude is None:
            longitude = "<MISSING>"

        if hours_of_operation == "":
            hours_of_operation = "<MISSING>"

        if location_type == "":
            location_type = "<MISSING>"

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
