# -*- coding: utf-8 -*-
import csv
from sgrequests import SgRequests
from sglogging import sglog
import json

website = "shopwss.com"
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

    search_url = "https://www.shopwss.com/store-locator/stores/ajax.json"
    stores_req = session.get(search_url, headers=headers)
    stores = json.loads(stores_req.text)["payload"]["United States"]
    for store in stores:
        if "DEFAULT_WEB_STORE" != store["name"]:
            page_url = "https://www.shopwss.com/store-locator/stores/" + str(
                store["id"]
            )
            locator_domain = website
            location_name = store["name"].split("-")[1].strip()
            store_number = store["name"].split("-")[0].replace("Store", "").strip()

            if location_name == "":
                location_name = "<MISSING>"

            street_address = store["address1"]
            city = store["city"]
            state = store["countryRegions"][0]
            zip = store["postcode"]
            country_code = store["countryIso2"]["value"]

            if street_address == "":
                street_address = "<MISSING>"

            if city == "":
                city = "<MISSING>"

            if state == "":
                state = "<MISSING>"

            if zip == "":
                zip = "<MISSING>"

            phone = store["phone"]

            location_type = "<MISSING>"
            latitude = store["latitude"]
            longitude = store["longitude"]

            if latitude == "" or latitude is None:
                latitude = "<MISSING>"
            if longitude == "" or longitude is None:
                longitude = "<MISSING>"

            if phone == "" or phone is None:
                phone = "<MISSING>"

            hours_of_operation = (
                "Mon:" + store["monOpenTimes"] + " "
                "Tue:" + store["tueOpenTimes"] + " "
                "Wed:" + store["wedOpenTimes"] + " "
                "Thu:" + store["thuOpenTimes"] + " "
                "Fri:" + store["friOpenTimes"] + " "
                "Sat:" + store["satOpenTimes"] + " "
                "Sun:" + store["sunOpenTimes"]
            )

            if hours_of_operation == "" or hours_of_operation is None:
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
