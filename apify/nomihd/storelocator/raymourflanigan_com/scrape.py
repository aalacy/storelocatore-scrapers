# -*- coding: utf-8 -*-
import csv
from sgrequests import SgRequests
from sglogging import sglog
import json

website = "raymourflanigan.com"
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
    loc_list = []

    search_url = (
        "https://www.raymourflanigan.com/api/custom/location-search"
        "?postalCode=11236&distance=100000&includeShowroom"
        "Locations=true&includeOutletLocations=true&include"
        "ClearanceLocations=true&includeAppointments=true"
    )

    stores_req = session.get(search_url, headers=headers)
    stores = json.loads(stores_req.text)["locations"]
    for store_json in stores:
        page_url = "https://www.raymourflanigan.com" + store_json["url"]
        locator_domain = website
        location_name = store_json["displayName"]
        street_address = store_json["addressLine1"]
        city = store_json["city"]
        state = store_json["stateProvince"]
        zip = store_json["postalCode"]
        country_code = ""

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

        store_number = store_json["businessUnitCode"]
        phone = store_json["phoneNumber"]

        location_type = "<MISSING>"
        hours_of_operation = ""
        hours = store_json["hours"]
        for day, hour in hours.items():
            if (
                hours[day] is not None
                and hours[day]["open"] is not None
                and hours[day]["close"] is not None
            ):
                hours_of_operation = (
                    hours_of_operation
                    + day
                    + ":"
                    + hours[day]["open"]
                    + "-"
                    + hours[day]["close"]
                    + ""
                )
        hours_of_operation = hours_of_operation.strip()

        latitude = store_json["latitude"]
        longitude = store_json["longitude"]

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

        # break
    return loc_list


def scrape():
    log.info("Started")
    data = fetch_data()
    write_output(data)
    log.info("Finished")


if __name__ == "__main__":
    scrape()
