# -*- coding: utf-8 -*-
import csv
from sgrequests import SgRequests
from sglogging import sglog
import json
import lxml.html

website = "clubfitness.us"
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

    search_url = "https://www.clubfitness.us/wp-admin/admin-ajax.php?action=store_search&lat=38.627003&lng=-90.199404&max_results=50000&search_radius=50000&autoload=1"
    stores_req = session.get(search_url, headers=headers)
    stores = json.loads(stores_req.text)

    for store in stores:
        page_url = store["permalink"]
        locator_domain = website
        location_name = (
            store["store"]
            .replace("&#8217;", "'")
            .replace("&#8211;", "-")
            .strip()
            .replace("&#038;", "&")
            .strip()
        )
        if location_name == "":
            location_name = "<MISSING>"

        street_address = store["address"]
        if store["address2"] is not None and len(store["address2"]) > 0:
            street_address = street_address + ", " + store["address2"]

        street_address = (
            street_address.encode("ascii", "replace")
            .decode("utf-8")
            .replace("?", "'")
            .strip()
        )
        city = store["city"]
        state = store["state"]
        zip = store["zip"]

        country_code = store["country"]
        if street_address == "" or street_address is None:
            street_address = "<MISSING>"

        if city == "" or city is None:
            city = "<MISSING>"

        if state == "" or state is None:
            state = "<MISSING>"

        if zip == "" or zip is None:
            zip = "<MISSING>"

        store_number = str(store["id"])
        phone = store["phone"]

        location_type = "<MISSING>"
        hours_list = []
        if store["hours"] is not None and len(store["hours"]) > 0:
            hours = lxml.html.fromstring(store["hours"]).xpath("//tr")
            hours_list = []
            hours_of_operation = ""
            for hour in hours:
                day = "".join(hour.xpath("td[1]/text()")).strip()
                time = "".join(hour.xpath("td[2]//text()")).strip()
                hours_list.append(day + ":" + time)

        hours_of_operation = "; ".join(hours_list).strip()

        latitude = store["lat"]
        longitude = store["lng"]

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
