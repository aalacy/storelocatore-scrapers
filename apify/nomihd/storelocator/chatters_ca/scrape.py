# -*- coding: utf-8 -*-
import csv
from sgrequests import SgRequests
from sglogging import sglog
import json

website = "chatters.ca"
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

    search_url = "https://locations.chatters.ca/"
    stores_req = session.get(search_url, headers=headers)
    json_text = (
        '{"features":[{"type":'
        + stores_req.text.split('"features":[{"type":')[1]
        .strip()
        .split("]}}]}")[0]
        .strip()
        + "]}}]}"
    )

    stores = json.loads(json_text)["features"]
    for store in stores:
        store_number = str(store["properties"]["id"])
        page_url = "https://locations.chatters.ca/" + store["properties"]["slug"]
        log.info(f"Pulling data for ID: {store_number}")
        store_req = session.get(
            "https://sls-api-service.sweetiq-sls-production-west.sweetiq.com/7d0Vk88cVVHEpawHrS6e3bze3pbkWY/locations-details?locale=en_CA&ids="
            + store_number
            + "&clientId=5de977cea324c2c365a2576b&cname=locations.chatters.ca",
            headers=headers,
        )
        store_json = json.loads(store_req.text)["features"][0]
        latitude = store_json["geometry"]["coordinates"][1]
        longitude = store_json["geometry"]["coordinates"][0]

        location_name = store_json["properties"]["name"]

        locator_domain = website

        location_type = "<MISSING>"

        street_address = store_json["properties"]["addressLine1"]
        if (
            store_json["properties"]["addressLine2"] is not None
            and len(store_json["properties"]["addressLine2"]) > 0
        ):
            street_address = (
                street_address + ", " + store_json["properties"]["addressLine2"]
            )

        city = store_json["properties"]["city"]
        state = store_json["properties"]["province"]
        zip = store_json["properties"]["postalCode"]
        country_code = store_json["properties"]["country"]
        phone = store_json["properties"]["phoneLabel"]
        hours_of_operation = ""
        hours_list = []
        hours = store_json["properties"]["hoursOfOperation"]
        for day in hours.keys():
            time = ""
            if len(hours[day]) > 0:
                time = str(hours[day][0][0]) + "-" + str(hours[day][0][1])
            else:
                time = "Closed"

            hours_list.append(day + ":" + time)

        hours_of_operation = "; ".join(hours_list).strip()

        if store_number == "":
            store_number = "<MISSING>"

        if location_name == "":
            location_name = "<MISSING>"

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

        if phone == "" or phone is None:
            phone = "<MISSING>"

        if latitude == "" or latitude is None:
            latitude = "<MISSING>"
        if longitude == "" or longitude is None:
            longitude = "<MISSING>"

        if hours_of_operation == "":
            hours_of_operation = "<MISSING>"

        if location_type == "":
            location_type = "<MISSING>"

        if store_json["properties"]["isPermanentlyClosed"] is not True:
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
