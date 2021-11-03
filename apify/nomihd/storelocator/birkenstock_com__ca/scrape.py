# -*- coding: utf-8 -*-
import csv
from sgrequests import SgRequests
from sglogging import sglog
import json

website = "birkenstock.com/ca"
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

    search_url = "https://www.birkenstock.com/on/demandware.store/Sites-CA-Site/en_CA/Stores-GetStoresJson?latitude=45.447480&longitude=-73.441440&latituderef=45.447480&longituderef=-73.441440&storeid=&distance=19&distanceunit=mi&searchText=&countryCode=CA&storeLocatorType=regular"
    stores_req = session.get(search_url, headers=headers)
    stores = json.loads(stores_req.text)["stores"]

    for key in stores.keys():
        page_url = "<MISSING>"
        locator_domain = website
        location_name = stores[key]["name"]
        if location_name == "":
            location_name = "<MISSING>"

        street_address = stores[key]["address1"]
        city = stores[key]["city"]
        state = stores[key]["state"]
        zip = stores[key]["postalCode"]
        country_code = stores[key]["countryCode"]
        if street_address == "" or street_address is None:
            street_address = "<MISSING>"

        if city == "" or city is None:
            city = "<MISSING>"

        if state == "" or state is None:
            state = "<MISSING>"

        if zip == "" or zip is None:
            zip = "<MISSING>"

        store_number = "<MISSING>"
        phone = "".join(stores[key]["phoneAreaCode"][:3]) + " " + stores[key]["phone"]
        location_type = "<MISSING>"
        hours_of_operation = stores[key]["storeHoursHTML"]

        latitude = stores[key]["latitude"]
        longitude = stores[key]["longitude"]

        if latitude == "" or latitude is None:
            latitude = "<MISSING>"
        if longitude == "" or longitude is None:
            longitude = "<MISSING>"

        if hours_of_operation == "" or hours_of_operation is None:
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

        # break
    return loc_list


def scrape():
    log.info("Started")
    data = fetch_data()
    write_output(data)
    log.info("Finished")


if __name__ == "__main__":
    scrape()
