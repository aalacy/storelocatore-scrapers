# -*- coding: utf-8 -*-
import csv
from sgrequests import SgRequests
from sglogging import sglog
import json
import us
import lxml.html
from bs4 import BeautifulSoup

website = "unionbank.com"
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
    locator_domain = website
    page_url = ""
    location_name = ""
    street_address = ""
    city = ""
    state = ""
    zip = ""
    country_code = ""
    store_number = "<MISSING>"
    phone = ""
    location_type = ""
    latitude = ""
    longitude = ""
    hours_of_operation = ""
    loc_list = []

    stores_req = session.get(
        "https://www.unionbank.com/locations/all",
        headers=headers,
    )
    stores_sel = lxml.html.fromstring(stores_req.text)
    stores = stores_sel.xpath(
        '//div[@class="accordion__expansion-panel"]'
        '//div[@class="component__container"]/div/p'
    )
    for store in stores:

        if location_type == "":
            location_type = "<MISSING>"
        raw_text = store.xpath("text()")
        if len(raw_text) > 0:
            street_address = raw_text[0].strip()
        if street_address == "":
            street_address = "<MISSING>"

        city_state_zip = ""
        if len(raw_text) > 1:
            city_state_zip = raw_text[1]

        city = city_state_zip.split(",")[0].strip()
        state = city_state_zip.split(",")[1].strip().split(" ")[0].strip()
        zip = city_state_zip.split(",")[1].strip().split(" ")[1].strip()

        if len(raw_text) > 2:
            phone = raw_text[2].replace("Tel:", "").strip()

        if phone == "":
            phone = "<MISSING>"

        if us.states.lookup(state):
            country_code = "US"

        if country_code == "":
            country_code = "<MISSING>"

        if len(store.xpath(".//a/@href")) > 0:
            page_url = "".join(store.xpath(".//a/@href")).strip()
            if "unionbank.com" not in page_url:
                page_url = "https://www.unionbank.com" + page_url

            s_req = session.get(page_url, headers=headers)
            store_sel = lxml.html.fromstring(s_req.text)
            location_name = "".join(store.xpath(".//a//text()")).strip()
            map_url = "".join(
                store_sel.xpath(
                    '//div[@class="btn btn--transparentWhiteText"]' "/a/@href"
                )
            ).strip()
            if len(map_url) > 0 and "@" in map_url:
                latitude = map_url.split("@")[1].strip().split(",")[0].strip()
                longitude = map_url.split("@")[1].strip().split(",")[1].strip()
            else:
                latitude = "<MISSING>"
                longitude = "<MISSING>"

            hours_of_operation = (
                " ".join(
                    store_sel.xpath(
                        '//div[@class="text-block-with-list__list"]' "/ul/li/p//text()"
                    )
                )
                .strip()
                .replace("\xa0", "")
            )

        else:
            page_url = "<MISSING>"
            location_name = "".join(store.xpath("strong/text()")).strip()
            latitude = "<MISSING>"
            longitude = "<MISSING>"
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

    return loc_list


def scrape():
    log.info("Started")
    data = fetch_data()
    write_output(data)
    log.info("Finished")


if __name__ == "__main__":
    scrape()
