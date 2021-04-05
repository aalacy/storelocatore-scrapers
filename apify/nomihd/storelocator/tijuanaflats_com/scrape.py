# -*- coding: utf-8 -*-
import csv
from sgrequests import SgRequests
from sglogging import sglog
import json
import us

website = "tijuanaflats.com"
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

    search_url = "https://www.tijuanaflats.com/locations"
    stores_req = session.get(search_url, headers=headers)
    stores = json.loads(
        stores_req.text.split('locations="')[1]
        .strip()
        .split('" inline-template')[0]
        .strip()
        .replace("&quot;", '"')
        .replace("&quoquot;", '"')
        .strip()
    )
    for store in stores:
        page_url = "https://" + store["link"].replace("https://api.", "").strip()
        locator_domain = website
        location_name = (
            store["title"]["rendered"]
            .replace("&amp;#038;", "&")
            .strip()
            .replace("&amp;#8211;", "-")
            .replace("&amp;#8217;", "'")
        )
        if location_name == "":
            location_name = "<MISSING>"

        street_address = store["acf"]["address_1"]
        city = store["acf"]["city"]
        state = store["acf"]["state"]
        zip = store["acf"]["zip"]
        country_code = "<MISSING>"
        if us.states.lookup(state):
            country_code = "US"

        if street_address == "":
            street_address = "<MISSING>"

        if city == "":
            city = "<MISSING>"

        if state == "":
            state = "<MISSING>"

        if zip == "":
            zip = "<MISSING>"

        store_number = str(store["id"])
        phone = store["acf"]["contact_phone"]

        location_type = "<MISSING>"
        hours_of_operation = " ".join(
            store["acf"]["hours_of_operation"]
            .replace("&lt;br /&gt;", "")
            .strip()
            .split("\n")
        ).strip()

        latitude = store["acf"]["physical_location"]["lat"]
        longitude = store["acf"]["physical_location"]["lng"]

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
