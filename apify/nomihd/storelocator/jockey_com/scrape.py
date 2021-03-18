# -*- coding: utf-8 -*-
import csv
from sgrequests import SgRequests
from sglogging import sglog
import json

website = "jockey.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "authority": "www.jockey.com",
    "cache-control": "max-age=0",
    "sec-ch-ua": '"Chromium";v="88", "Google Chrome";v="88", ";Not A Brand";v="99"',
    "sec-ch-ua-mobile": "?0",
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36",
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

    search_url = "https://www.jockey.com/shoppingguide/storelocator"
    stores_req = session.get(search_url, headers=headers)
    stores = json.loads(
        stores_req.text.split("allStores:")[1].strip().split("}]}")[0].strip() + "}]"
    )
    for store in stores:
        page_url = search_url
        locator_domain = website
        location_name = store["AddressLine2"]
        if location_name == "":
            location_name = "<MISSING>"

        street_address = store["AddressLine1"]
        city = store["City"]
        state = store["State"]
        zip = store["PostalCode"]

        country_code = store["CountryCode"]

        if street_address == "":
            street_address = "<MISSING>"

        if city == "":
            city = "<MISSING>"

        if state == "":
            state = "<MISSING>"

        if zip == "":
            zip = "<MISSING>"

        store_number = str(store["StoreCode"])
        phone = store["MainPhone"]

        location_type = "<MISSING>"
        hours_of_operation = store["Hours"].replace(",", " ").strip()
        try:
            hours_of_operation = " ".join(hours_of_operation.split("\n")).strip()
        except:
            pass
        latitude = store["Latitude"]
        longitude = store["Longitude"]

        if latitude == "":
            latitude = "<MISSING>"
        if longitude == "":
            longitude = "<MISSING>"

        if hours_of_operation == "":
            hours_of_operation = "<MISSING>"

        if phone is None:
            phone = "<MISSING>"

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
