# -*- coding: utf-8 -*-
import csv
from sgrequests import SgRequests
from sglogging import sglog
import lxml.html
import json

website = "pizzajoes.com"
session = SgRequests()
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36",
    "Accept": "*/*",
    "X-Requested-With": "XMLHttpRequest",
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

    search_url = "https://www.pizzajoes.com/our-locations/"
    stores_req = session.get(search_url, headers=headers)
    stores_sel = lxml.html.fromstring(stores_req.text)
    stores = stores_sel.xpath('//h2[@class="geodir-entry-title "]/a/@href')
    for store_url in stores:
        page_url = store_url.strip()
        locator_domain = website
        log.info(page_url)

        store_req = session.get(page_url, headers=headers)
        store_sel = lxml.html.fromstring(store_req.text)
        json_list = store_sel.xpath('//script[@type="application/ld+json"]/text()')
        for js in json_list:
            if "streetAddress" in js:
                json_text = js
                store_json = json.loads(json_text)

                location_name = store_json["name"]
                if location_name == "":
                    location_name = "<MISSING>"

                street_address = store_json["address"]["streetAddress"]
                city = store_json["address"]["addressLocality"]
                state = store_json["address"]["addressRegion"]
                zip = store_json["address"]["postalCode"]
                country_code = store_json["address"]["addressCountry"]

                if country_code == "" or country_code is None:
                    country_code = "<MISSING>"
                if street_address == "":
                    street_address = "<MISSING>"

                if city == "":
                    city = "<MISSING>"

                if state == "":
                    state = "<MISSING>"

                if zip == "":
                    zip = "<MISSING>"

                store_number = "<MISSING>"
                phone = store_json["telephone"]

                location_type = "<MISSING>"

                hours_of_operation = ""
                hours_list = []
                try:
                    hours = store_json["openingHours"]
                    for hour in hours:
                        if len("".join(hour).strip()) > 0:
                            hours_list.append("".join(hour).strip())
                except:
                    pass
                hours_of_operation = "; ".join(hours_list).strip()

                latitude = store_json["geo"]["latitude"]
                longitude = store_json["geo"]["longitude"]

                if latitude == "":
                    latitude = "<MISSING>"
                if longitude == "":
                    longitude = "<MISSING>"

                if hours_of_operation == "":
                    hours_of_operation = "<MISSING>"
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
