# -*- coding: utf-8 -*-
import csv
from sgrequests import SgRequests
from sglogging import sglog
import json

website = "travisperkins.co.uk"
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

    search_url = "https://www.travisperkins.co.uk/branch-locator"
    stores_req = session.get(search_url, headers=headers)
    stores = json.loads(
        stores_req.text.split("window.__PRELOADED_STATE__ = ")[1]
        .strip()
        .split("</script>")[0]
        .strip()
    )["branch"]["allBranches"]

    for store in stores:
        page_url = "https://www.travisperkins.co.uk/branch-locator/" + store["code"]

        locator_domain = website
        location_name = store["name"]
        if location_name == "":
            location_name = "<MISSING>"

        street_address = store["address"]["line1"].strip()

        if store["address"]["line2"] is not None:
            street_address = street_address + ", " + store["address"]["line2"]

        if store["address"]["line3"] is not None:
            street_address = street_address + ", " + store["address"]["line3"]

        city = store["address"]["town"].strip()
        state = "<MISSING>"
        zip = store["address"]["postalCode"].strip()
        country_code = "GB"

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

        store_number = store["code"]
        phone = store["phone"].strip()

        location_type = "<MISSING>"

        latitude = store["geoPoint"]["lat"]
        longitude = store["geoPoint"]["lng"]

        if latitude == "" or latitude is None:
            latitude = "<MISSING>"
        if longitude == "" or longitude is None:
            longitude = "<MISSING>"

        hours_of_operation = ""

        hours = store["branchSchedule"]
        hours_list = []
        for hour in hours:
            day = hour["dayOfWeek"]
            if hour["closed"] is True:
                time = "Closed"
            else:
                time = hour["openingTime"] + "-" + hour["closingTime"]

            hours_list.append(day + ":" + time)

        hours_of_operation = "; ".join(hours_list).strip()
        if hours_of_operation == "":
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

    return loc_list


def scrape():
    log.info("Started")
    data = fetch_data()
    write_output(data)
    log.info("Finished")


if __name__ == "__main__":
    scrape()
