# -*- coding: utf-8 -*-
import csv
from sgrequests import SgRequests
from sglogging import sglog
import json

website = "carterlumber.com"
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

    data = {
        "radius": "1000000",
        "address": "10001",
        "lat": "40.75368539999999",
        "lng": "-73.9991637",
        "loc_type": "postal_code",
        "long_name": "10001",
        "short_name": "10001",
        "formatted_name": "New York, NY 10001, USA",
    }

    search_url = "https://www.carterlumber.com/ustorelocator/location/searchJson"
    stores_req = session.post(search_url, data=data, headers=headers)
    stores = json.loads(stores_req.text)["markers"]
    for store in stores:
        page_url = "https://www.carterlumber.com/store-information?id=" + str(
            store["location_id"]
        )
        locator_domain = website
        location_name = store["title"]
        if location_name == "":
            location_name = "<MISSING>"

        if "<p>" in store["address_display"]:
            street_address = (
                store["address_display"]
                .split("<p>", 1)[1]
                .strip()
                .split("<")[0]
                .strip()
            )

        city = store["city"]
        state = store["state"]
        zip = store["zip"]
        country_code = store["country"]
        if country_code == "":
            country_code = "<MISSING>"

        if street_address == "":
            street_address = "<MISSING>"

        if city == "":
            city = "<MISSING>"

        if state == "":
            state = "<MISSING>"

        if zip == "":
            zip = "<MISSING>"

        street_address = (
            street_address.replace(city + ",", "")
            .replace(state, "")
            .replace(zip, "")
            .strip()
        )

        store_number = str(store["location_id"])
        phone = store["phone"]

        location_type = "<MISSING>"
        hours_of_operation = ""
        if "Closed until further notice" == store["weekday_hours"]:
            location_type = "Closed until further notice"
        elif "Appointment ONLY" == store["weekday_hours"]:
            location_type = "Appointment ONLY"
        elif "Closed to the Public" == store["weekday_hours"]:
            location_type = "Closed to the Public"
        elif "Appointment ONLY" == store["weekday_hours"]:
            location_type = "Appointment ONLY"

        else:
            if len(store["weekday_hours"]) > 0:
                hours_of_operation = hours_of_operation + store["weekday_hours"] + " "
            if len(store["saturday_hours"]) > 0:
                hours_of_operation = hours_of_operation + store["saturday_hours"] + " "
            if len(store["sunday_hours"]) > 0:
                hours_of_operation = hours_of_operation + store["sunday_hours"] + " "

        hours_of_operation = hours_of_operation.strip()

        latitude = store["latitude"]
        longitude = store["longitude"]

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
