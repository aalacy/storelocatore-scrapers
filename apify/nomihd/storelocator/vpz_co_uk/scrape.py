# -*- coding: utf-8 -*-
import csv
from sgrequests import SgRequests
from sglogging import sglog
import json

website = "vpz.co.uk"
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

    search_url = "https://liveapi.yext.com/v2/accounts/me/entities/geosearch?radius=2500&location=SW17%200RG&offset={}&limit=50&api_key=46014f43cb3d0581a9d4b5e3c04e0b4e&v=20181201&resolvePlaceholders=true&entityTypes=location"
    offset = 0
    while True:
        final_url = search_url.format(str(offset))
        stores_req = session.get(final_url, headers=headers)
        json_data = json.loads(stores_req.text)
        if json_data["response"]["count"] < offset:
            break

        stores = json_data["response"]["entities"]
        for store in stores:
            page_url = "<MISSING>"
            if "landingPageUrl" in store:
                page_url = store["landingPageUrl"]

            locator_domain = website
            location_name = store["name"]
            if location_name == "":
                location_name = "<MISSING>"

            street_address = store["address"]["line1"]
            if "line2" in store:
                if store["line2"] is not None and len(store["line2"]) > 0:
                    street_address = street_address + ", " + store["line2"]

            city = store["address"]["city"]
            state = "<MISSING>"
            if "region" in store["address"]:
                state = store["address"]["region"]
            zip = store["address"]["postalCode"]
            country_code = store["address"]["countryCode"]

            if street_address == "":
                street_address = "<MISSING>"

            if city == "":
                city = "<MISSING>"

            if state == "":
                state = "<MISSING>"

            if zip == "":
                zip = "<MISSING>"

            store_number = store["meta"]["id"]
            phone = store["mainPhone"]

            location_type = "open"

            if "closed" in store:
                if store["closed"] is True:
                    location_type = "closed"

            hours = store["hours"]
            hours_of_operation = ""
            for day, time in hours.items():
                if "openIntervals" in time:
                    hours_of_operation = (
                        hours_of_operation
                        + day
                        + ":"
                        + time["openIntervals"][0]["start"]
                        + "-"
                        + time["openIntervals"][0]["end"]
                        + " "
                    )

            hours_of_operation = hours_of_operation.strip()

            latitude = store["yextDisplayCoordinate"]["latitude"]
            longitude = store["yextDisplayCoordinate"]["longitude"]

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

        offset = offset + 50
        # break
    return loc_list


def scrape():
    log.info("Started")
    data = fetch_data()
    write_output(data)
    log.info("Finished")


if __name__ == "__main__":
    scrape()
