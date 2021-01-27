# -*- coding: utf-8 -*-
import csv
from sgrequests import SgRequests
from sglogging import sglog
import json
from bs4 import BeautifulSoup as BS
import lxml.html

website = "pancheros.com"
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

    search_url = "https://www.pancheros.com/index.php?ACT=23&locate_method=json&lat=40.75368539999999&lng=-73.9991637&radius=1000000"
    stores_req = session.get(search_url, headers=headers)
    stores = stores_req.json()
    for store in stores:
        page_url = "https://www.pancheros.com/locations/" + store["url_title"]

        locator_domain = website
        location_name = store["title"]
        if location_name == "":
            location_name = "<MISSING>"

        address = json.loads(store["store_address"])
        street_address = address["street"].strip()
        if "street_2" in address:
            street_2 = address["street_2"]
            if len(street_2) > 0:
                street_address = street_address + ", " + street_2

        city = address["city"].strip()
        state = address["region"].strip().replace(",", "").strip()
        zip = address["postal_code"].strip()

        if state.isdigit():
            zip = state
            state = "<MISSING>"

        country_code = address["country"]

        if street_address == "" or street_address is None:
            street_address = "<MISSING>"

        if city == "" or city is None:
            city = "<MISSING>"

        if state == "" or state is None:
            state = "<MISSING>"

        if zip == "" or zip is None:
            zip = "<MISSING>"

        store_number = str(store["id"])
        phone = store["store_telephone"]

        location_type = "<MISSING>"
        if location_type == "" or location_type is None:
            location_type = "<MISSING>"

        latitude = store["lat"]
        longitude = store["lng"]

        if latitude == "" or latitude is None:
            latitude = "<MISSING>"
        if longitude == "" or longitude is None:
            longitude = "<MISSING>"

        hours_of_operation = ""
        temp_hours = BS(store["store_hours"], "html.parser").get_text().split("\n")

        if len("".join(temp_hours).strip()) <= 0:
            store_req = session.get(page_url, headers=headers)
            store_sel = lxml.html.fromstring(store_req.text)
            hours = store_sel.xpath('//tr[@class="LocationHours-day"]')
            hours_list = []
            for hour in hours:
                hours_list.append(
                    "".join(hour.xpath("th/text()")).strip()
                    + ":"
                    + "".join(hour.xpath("td/p/text()")).strip()
                )

            hours_of_operation = (
                ";".join(hours_list)
                .strip()
                .encode("ascii", "replace")
                .decode("utf-8")
                .replace("?", "")
                .strip()
            )

        else:
            hours = temp_hours
            hours_list = []
            for hour in hours:
                if len("".join(hour).strip()) > 0:
                    hours_list.append("".join(hour).strip())
            hours_of_operation = ";".join(hours_list).strip()

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
