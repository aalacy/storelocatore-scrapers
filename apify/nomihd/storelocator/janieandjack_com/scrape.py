# -*- coding: utf-8 -*-
import csv
from sgrequests import SgRequests
from sglogging import sglog
import us

website = "janieandjack.com"
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

    url = (
        "https://www.janieandjack.com/on/demandware.store/"
        "Sites-JanieAndJack-Site/en_US/Stores-GetNearestStores?latitude=31.4137"
        "&longitude=73.0805&countryCode=US&distanceUnit=mi&maxdistance=250000"
    )
    count = 0
    stores_req = None
    while count < 5:
        try:
            session = SgRequests()
            stores_req = session.get(url, headers=headers)
            count = 6
        except Exception:
            log.info(f"status_code:{str(stores_req.status_code)}")
            session = ""
            count += 1
            continue

    if count == 5:
        raise Exception("This should never happen")

    log.info(f"status_code:{str(stores_req.status_code)}")
    stores = stores_req.json()["stores"]
    for store in stores.keys():
        locator_domain = website
        location_name = stores[store]["name"]
        street_address = stores[store]["address1"]
        if len(stores[store]["address2"]) > 0:
            street_address = street_address + ", " + stores[store]["address2"]
        city = stores[store]["city"]
        state = stores[store]["stateCode"]
        zip = stores[store]["postalCode"]
        country_code = stores[store]["countryCode"]
        if country_code == "":
            if us.states.lookup(state):
                country_code = "US"

        page_url = (
            "https://www.janieandjack.com/on/demandware.store/"
            "Sites-JanieAndJack-Site/en_US/Stores-Details?StoreID=" + str(store)
        )
        phone = stores[store]["phone"]
        store_number = "<MISSING>"

        location_type = stores[store]["storeType"]
        if location_type == "":
            location_type = "<MISSING>"

        latitude = stores[store]["latitude"]
        longitude = stores[store]["longitude"]
        hours_of_operation = stores[store]["storeHours"].strip() + " "
        if len(stores[store]["storeHours2"].replace("&nbsp;", "").strip()) > 0:
            hours_of_operation = (
                hours_of_operation + stores[store]["storeHours2"].strip() + " "
            )
        if len(stores[store]["storeHours3"].replace("&nbsp;", "").strip()) > 0:
            hours_of_operation = (
                hours_of_operation + stores[store]["storeHours3"].strip() + " "
            )
        if len(stores[store]["storeHours4"].replace("&nbsp;", "").strip()) > 0:
            hours_of_operation = (
                hours_of_operation + stores[store]["storeHours4"].strip() + " "
            )
        if len(stores[store]["storeHours5"].replace("&nbsp;", "").strip()) > 0:
            hours_of_operation = (
                hours_of_operation + stores[store]["storeHours5"].strip() + " "
            )

        hours_of_operation = hours_of_operation.strip()
        if hours_of_operation == "":
            hours_of_operation = "<MISSING>"
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
