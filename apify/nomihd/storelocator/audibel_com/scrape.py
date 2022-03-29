# -*- coding: utf-8 -*-
import csv
from sgrequests import SgRequests
from sglogging import sglog
import json
from sgzip.dynamic import DynamicZipSearch, SearchableCountries

website = "audibel.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36"
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
    zips = DynamicZipSearch(
        country_codes=[SearchableCountries.USA], max_search_distance_miles=200
    )
    for zip_code in zips:
        log.info(f"{zip_code} | remaining: {zips.items_remaining()}")

        search_url = (
            "https://www.audibel.com/api/dealerservice/Audibel.com/{}/True/False/125"
        ).format(zip_code)
        stores_req = session.get(search_url, headers=headers)
        stores = json.loads(stores_req.text)["Locations"]
        for store_json in stores:
            if store_json["Country"] == "United States":
                page_url = "<MISSING>"
                locator_domain = website
                location_name = store_json["BusinessName"]
                street_address = store_json["StreetAddress"]
                city_state_zip = store_json["CityStateZip"]
                city = city_state_zip.split(",")[0].strip()
                state = city_state_zip.split(",")[1].strip().split(" ")[0].strip()
                zip = city_state_zip.split(",")[1].strip().split(" ")[1].strip()
                country_code = "US"

                if street_address == "":
                    street_address = "<MISSING>"

                if city == "":
                    city = "<MISSING>"

                if state == "":
                    state = "<MISSING>"

                if zip == "":
                    zip = "<MISSING>"

                if country_code == "":
                    country_code = "<MISSING>"

                store_number = "<MISSING>"
                phone = store_json["PhoneNumber"]

                location_type = "<MISSING>"
                hours_of_operation = "<MISSING>"

                latitude = store_json["Latitude"]
                longitude = store_json["Longitude"]
                zips.found_location_at(latitude, longitude)
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
                yield curr_list


def scrape():
    log.info("Started")
    data = fetch_data()
    write_output(data)
    log.info("Finished")


if __name__ == "__main__":
    scrape()
