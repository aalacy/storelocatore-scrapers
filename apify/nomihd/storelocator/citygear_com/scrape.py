# -*- coding: utf-8 -*-
import csv
from sgrequests import SgRequests
from sglogging import sglog
import json

website = "citygear.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "authority": "www.hibbett.com",
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

    url = (
        "https://www.hibbett.com/on/demandware.store/Sites-Hibbett-US-Site/"
        "default/Stores-GetNearestStores?latitude=42.4685771&"
        "longitude=-83.42107759999999&countryCode=US&distanceUnit=mi&maxdistance=2500000"
    )
    stores_req = session.get(
        url,
        headers=headers,
    )
    stores = json.loads(stores_req.text.strip())["stores"]
    for store in stores.keys():
        locator_domain = website
        location_name = stores[store]["name"]
        street_address = stores[store]["address1"]
        if len(stores[store]["address2"]) > 0:
            street_address = street_address + ", " + stores[store]["address2"]
        city = stores[store]["city"]
        state = stores[store]["stateCode"]
        zip = stores[store]["postalCode"]
        country_code = stores[store]["countryCode"]
        page_url = (
            "https://www.hibbett.com/storedetails/"
            + state
            + "/"
            + city
            + "/"
            + stores[store]["id"]
        )

        phone = stores[store]["phone"]
        store_number = "<MISSING>"

        location_type = "<MISSING>"
        if stores[store]["isOpeningSoon"] is True:
            location_type = "Opening Soon"

        if stores[store]["temporarilyClosed"] is True:
            location_type = "Temporarily Closed"

        latitude = stores[store]["latitude"]
        longitude = stores[store]["longitude"]
        hours_of_operation = stores[store]["storeHours"].replace("|", " ").strip()

        if hours_of_operation == "":
            hours_of_operation = "<MISSING>"
        if phone == "":
            phone = "<MISSING>"

        if country_code == "":
            country_code = "<MISSING>"

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
