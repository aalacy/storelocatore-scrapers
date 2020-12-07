# -*- coding: utf-8 -*-
import csv
from sgrequests import SgRequests
from sglogging import sglog
import json
import us

website = "mfa-inc.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "Connection": "keep-alive",
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "X-Requested-With": "XMLHttpRequest",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36",
    "Content-Type": "application/json; charset=UTF-8",
    "Origin": "https://storelocator.mfa-inc.com",
    "Sec-Fetch-Site": "same-origin",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Dest": "empty",
    "Referer": "https://storelocator.mfa-inc.com/",
    "Accept-Language": "en-US,en-GB;q=0.9,en;q=0.8",
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


def get_location_type(id):

    if id == 3:
        return "AGChoice (Kansas)"
    if id == 4:
        return "Atchison County AGChoice"
    if id == 5:
        return "Morris Farm"
    if id == 6:
        return "West Central AGRIServices"
    if id == 7:
        return "MFA Agri Services"
    if id == 9:
        return "Central Missouri AGRIService"
    if id == 10:
        return "Local Affiliates"
    else:
        return "Local Affiliates"


def fetch_data():
    # Your scraper here
    locator_domain = website
    page_url = ""
    location_name = ""
    street_address = ""
    city = ""
    state = ""
    zip = ""
    country_code = ""
    store_number = ""
    phone = ""
    location_type = ""
    latitude = ""
    longitude = ""
    hours_of_operation = ""
    loc_list = []

    data = (
        '{"milesFrom":0,"fromLongitude":-73.9991637,"fromLatitude":40.75368539999999}'
    )

    stores_resp = session.post(
        "https://storelocator.mfa-inc.com/StoreService.svc/GetStoresByMiles",
        data=data,
        headers=headers,
    )
    stores_json = json.loads(stores_resp.text)["d"]
    for store in stores_json:
        page_url = "<MISSING>"
        store_number = str(store["_locationNum"])
        location_name = (
            store["_locationName"].strip() + " - " + str(store["_locationNum"])
        )
        street_address = store["_storeAddress"]
        if street_address == "":
            street_address = "<MISSING>"

        city = store["_city"]
        state = store["_state"]

        zip = store["_zip"]

        location_type = get_location_type(store["_managerListTypeId"])

        if location_type == "":
            location_type = "<MISSING>"

        latitude = store["_latitude"]
        longitude = store["_longitude"]

        if us.states.lookup(state):
            country_code = "US"

        if country_code == "":
            country_code = "<MISSING>"

        phone = store["_telephone"]
        if phone == "":
            phone = "<MISSING>"

        hours_of_operation = "<MISSING>"

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
