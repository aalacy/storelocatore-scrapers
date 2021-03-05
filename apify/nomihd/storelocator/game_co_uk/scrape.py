# -*- coding: utf-8 -*-
import csv
from sgrequests import SgRequests
from sglogging import sglog
import json
import lxml.html
from urllib.parse import quote

website = "game_co.uk"
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

    search_url = "https://storefinderapi.game.co.uk/api/game/stores"
    stores_req = session.get(search_url, headers=headers)
    results = json.loads(stores_req.text)

    for res in results:
        stores = res["stores"]
        for store in stores:
            page_url = str(store["StoreNumber"]) + "/" + store["StoreName"]
            page_url = "https://storefinder.game.co.uk/game/stores/" + quote(page_url)

            log.info(page_url)

            locator_domain = website

            store_number = str(store["StoreNumber"])

            store_resp = session.get(page_url, headers=headers)
            store_sel = lxml.html.fromstring(store_resp.text)
            store_json = json.loads(
                "".join(
                    store_sel.xpath('//script[@type="application/ld+json"]/text()')
                ).strip()
            )
            location_name = store_json["name"]
            if location_name == "":
                location_name = "<MISSING>"

            street_address = store_json["address"]["streetAddress"]
            city = store_json["address"]["addressLocality"]
            state = store_json["address"]["addressRegion"]
            zip = store_json["address"]["postalCode"]

            country_code = "GB"

            if street_address == "" or street_address is None:
                street_address = "<MISSING>"

            if city == "" or city is None:
                city = "<MISSING>"

            if state == "" or state is None:
                state = "<MISSING>"

            if zip == "" or zip is None:
                zip = "<MISSING>"

            phone = store_json["telephone"]

            location_type = "<MISSING>"
            hours_of_operation = "<MISSING>"
            hour_list = []
            try:
                hours = store_json["openingHours"]
                for hour in hours:
                    hour_list.append(hour.replace('"', "").strip())
            except:
                pass

            hours_of_operation = ";".join(hour_list).strip()

            latitude = store_json["geo"]["latitude"]
            longitude = store_json["geo"]["longitude"]

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

    return loc_list


def scrape():
    log.info("Started")
    data = fetch_data()
    write_output(data)
    log.info("Finished")


if __name__ == "__main__":
    scrape()
