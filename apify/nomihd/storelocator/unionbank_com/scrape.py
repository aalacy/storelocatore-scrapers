# -*- coding: utf-8 -*-
import csv
from sgrequests import SgRequests
from sglogging import sglog
import us
import json
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
    loc_list = []

    url = (
        "https://drupal-prd.unionbank.com/rest/branch-locator"
        "?field_geocoordinates_proximity-lat=35.4516124"
        "&field_geocoordinates_proximity-lng=-118.7897558"
        "&field_geocoordinates_proximity=10000"
        "&field_geocoordinates_proximity_1-lat=35.4516124"
        "&field_geocoordinates_proximity_1-lng=-118.7897558"
        "&field_geocoordinates_proximity_1=10000"
    )
    stores_req = session.get(
        url,
        headers=headers,
    )
    json_data = json.loads(stores_req.text)
    for data in json_data:
        if "branchLocations" in data:
            stores = data["branchLocations"]
            for store in stores:
                locator_domain = website
                page_url = "<MISSING>"
                location_name = store["branchInfo"]["branchName"]
                street_address = store["branchInfo"]["address"]["addressLine"][0]
                city = store["branchInfo"]["address"]["city"]
                state = store["branchInfo"]["address"]["state"]
                zip = store["branchInfo"]["address"]["zipcode"]
                country_code = ""
                if us.states.lookup(state):
                    country_code = "US"

                phone = ""
                store_number = store["branchInfo"]["branchId"]
                if "phone" in store["branchInfo"]:
                    phone = store["branchInfo"]["phone"].replace("\xa0", "").strip()
                else:
                    phone = "<MISSING>"

                location_type = "<MISSING>"
                latitude = store["branchInfo"]["latitude"]
                longitude = store["branchInfo"]["longitude"]
                hours_of_operation = ""
                hours = store["branchHours"]
                for hour in hours:
                    hours_of_operation = (
                        hours_of_operation
                        + hour["displayLabel"]
                        + ":"
                        + hour["displayHours"]
                        + " "
                    )

                if hours_of_operation == "":
                    hours_of_operation = "<MISSING>"
                hours_of_operation = BeautifulSoup(
                    hours_of_operation.strip(), "html.parser"
                ).getText()
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
