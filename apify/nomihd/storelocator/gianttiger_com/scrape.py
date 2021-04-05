# -*- coding: utf-8 -*-
import csv
from sgrequests import SgRequests
from sglogging import sglog
import json

website = "gianttiger.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()

headers = {
    "authority": "www.gianttiger.com",
    "cache-control": "max-age=0",
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "sec-fetch-site": "none",
    "sec-fetch-mode": "navigate",
    "sec-fetch-user": "?1",
    "sec-fetch-dest": "document",
    "accept-language": "en-US,en-GB;q=0.9,en;q=0.8",
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

    session.get("https://www.gianttiger.com/").text
    stores_req = session.get(
        "https://www.gianttiger.com/api/commerce/storefront/locationUsageTypes/SP/locations/?pageSize=1000",
        headers=headers,
    )
    stores = json.loads(stores_req.text)["items"]

    for store in stores:
        locator_domain = website
        page_url = "<MISSING>"

        location_name = store["name"]
        street_address = store["address"]["address1"]
        city = store["address"]["cityOrTown"]
        state = store["address"]["stateOrProvince"]
        zip = store["address"]["postalOrZipCode"]

        if street_address == "":
            street_address = "<MISSING>"

        if city == "":
            city = "<MISSING>"

        if state == "":
            state = "<MISSING>"

        if zip == "":
            zip = "<MISSING>"

        country_code = store["address"]["countryCode"]

        store_number = store["code"]
        phone = store["phone"]
        location_type = store["locationTypes"][0]["name"]
        latitude = store["geo"]["lat"]
        longitude = store["geo"]["lng"]

        hours_of_operation = ""
        hours_dict = store["regularHours"]
        for day, hours in hours_dict.items():
            if day != "timeZone":
                if store["regularHours"][day]["isClosed"]:
                    hours_of_operation = hours_of_operation + day + ": Closed "
                else:
                    hours_of_operation = (
                        hours_of_operation
                        + day
                        + ": "
                        + store["regularHours"][day]["label"]
                        + " "
                    )

        hours_of_operation = hours_of_operation.strip()
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
        # break

    return loc_list


def scrape():
    log.info("Started")
    data = fetch_data()
    write_output(data)
    log.info("Finished")


if __name__ == "__main__":
    scrape()
