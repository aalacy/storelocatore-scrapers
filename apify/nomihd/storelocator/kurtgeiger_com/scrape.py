# -*- coding: utf-8 -*-
import csv
from sgrequests import SgRequests
from sglogging import sglog
import json

website = "kurtgeiger.com"
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

    search_url = "https://live-svc-storesinfo.kurtgeiger.com/LATEST/stores/isEnabled/1"
    stores_req = session.get(search_url, headers=headers)
    stores = json.loads(stores_req.text)
    for store_json in stores:
        if store_json["type"].lower().strip() == "store":
            page_url = "https://www.kurtgeiger.com/storelocator"

            latitude = store_json["latitude"]
            longitude = store_json["longitude"]

            location_name = store_json["name"].upper()

            locator_domain = website

            location_type = "<MISSING>"

            street_address = store_json["streetLine1"]
            if (
                store_json["streetLine2"] is not None
                and len(store_json["streetLine2"]) > 0
            ):
                street_address = street_address + ", " + store_json["streetLine2"]

            if (
                store_json["streetLine3"] is not None
                and len(store_json["streetLine3"]) > 0
            ):
                street_address = street_address + ", " + store_json["streetLine3"]

            city = store_json["town"]
            state = "<MISSING>"
            zip = store_json["postcode"]
            country_code = store_json["country"]
            phone = store_json["phone"]
            hours_of_operation = ""
            hours_list = []
            hours = store_json["openingHours"]
            for hour in hours:
                day = hour["day"]
                time = ""
                if hour["isClosed"] == 1:
                    time = "Closed"
                else:
                    time = hour["openingTime"] + "-" + hour["closingTime"]
                hours_list.append(day + ":" + time)

            hours_of_operation = "; ".join(hours_list).strip()

            store_number = str(store_json["id"])
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
