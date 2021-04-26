# -*- coding: utf-8 -*-
import csv
from sgrequests import SgRequests
from sglogging import sglog
import json

website = "coop.co.uk/funeralcare"
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

    search_url = "https://www.coop.co.uk/funeralcare/funeral-directors/api/locations/funeralcare?location=51.5073509%2C-0.1277583&distance=10000000&min_distance=0&min_results=5&format=json&page={}"
    page_no = 1
    while True:
        stores_req = session.get(search_url.format(str(page_no)), headers=headers)
        stores = json.loads(stores_req.text)["results"]
        for store_json in stores:
            page_url = "https://www.coop.co.uk" + store_json["url"]
            latitude = store_json["position"]["y"]
            longitude = store_json["position"]["x"]

            location_name = store_json["name"]

            locator_domain = website

            location_type = store_json["open_status"]

            street_address = store_json["street_address"]
            if (
                store_json["street_address2"] is not None
                and len(store_json["street_address2"]) > 0
            ):
                street_address = street_address + ", " + store_json["street_address2"]

            if (
                store_json["street_address3"] is not None
                and len(store_json["street_address3"]) > 0
            ):
                street_address = street_address + ", " + store_json["street_address3"]

            city = store_json["town"]
            state = store_json["county"]
            zip = store_json["postcode"]
            country_code = "GB"
            phone = store_json["phone"]
            hours_of_operation = ""
            hours_list = []
            hours = store_json["opening_hours"]
            for hour in hours:
                hours_list.append(hour["name"] + ":" + hour["label"])

            hours_of_operation = "; ".join(hours_list).strip()

            store_number = str(store_json["cedar"])
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

        if json.loads(stores_req.text)["next"] is None:
            break
        else:
            page_no = page_no + 1

    return loc_list


def scrape():
    log.info("Started")
    data = fetch_data()
    write_output(data)
    log.info("Finished")


if __name__ == "__main__":
    scrape()
