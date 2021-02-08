# -*- coding: utf-8 -*-
import csv
from sgrequests import SgRequests
from sglogging import sglog
import json

website = "jdwetherspoon.co.uk"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "Connection": "keep-alive",
    "sec-ch-ua": '"Google Chrome";v="87", " Not;A Brand";v="99", "Chromium";v="87"',
    "Accept": "application/json, text/plain, */*",
    # 'Request-Id': '|c7e8e7ea677740eda1e4b2d005230d0c.f0d48d57da094a63',
    "sec-ch-ua-mobile": "?0",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36",
    "Content-Type": "application/json;charset=UTF-8",
    "Origin": "https://www.jdwetherspoon.com",
    "Sec-Fetch-Site": "same-origin",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Dest": "empty",
    "Referer": "https://www.jdwetherspoon.com/pubs/all-pubs",
    "Accept-Language": "en-US,en-GB;q=0.9,en;q=0.8",
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

    data = '{"region":null,"paging":{"UsePagination":false},"facilities":[],"searchType":0}'
    search_url = "https://www.jdwetherspoon.com/api/advancedsearch"
    stores_req = session.post(search_url, data=data, headers=headers)
    regions = json.loads(stores_req.text)["regions"]
    for region in regions:
        subRegions = region["subRegions"]
        for sub in subRegions:
            stores = sub["items"]
            for store in stores:
                if store["PubIsClosed"] is False:
                    page_url = "https://www.jdwetherspoon.com" + store["url"]

                    locator_domain = website
                    location_name = store["name"]
                    if location_name == "":
                        location_name = "<MISSING>"

                    street_address = (
                        store["address1"]
                        .strip()
                        .encode("ascii", "replace")
                        .decode("utf-8")
                        .replace("?", "-")
                        .strip()
                    )
                    city = store["city"].strip()
                    state = store["county"].strip()
                    zip = store["postcode"].strip()
                    country_code = region["region"]

                    if country_code == "":
                        country_code = "<MISSING>"

                    if street_address == "" or street_address is None:
                        street_address = "<MISSING>"

                    if city == "" or city is None:
                        city = "<MISSING>"

                    if state == "" or state is None:
                        state = "<MISSING>"

                    if zip == "" or zip is None:
                        zip = "<MISSING>"

                    if country_code == "" or country_code is None:
                        country_code = "<MISSING>"

                    store_number = store["pubNumber"]
                    if store_number == "" or store_number is None:
                        store_number = "<MISSING>"

                    phone = store["telephone"]

                    location_type = "<MISSING>"
                    if "/pubs/" in page_url:
                        location_type = "pub"
                    elif "/hotels/" in page_url:
                        location_type = "hotel"

                    hours_of_operation = ""
                    if store["PubIsTemporaryClosed"] is True:
                        hours_of_operation = "Temporary Closed"

                    latitude = store["lat"]
                    longitude = store["lng"]

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
