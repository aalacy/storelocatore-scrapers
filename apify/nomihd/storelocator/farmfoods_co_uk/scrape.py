# -*- coding: utf-8 -*-
import csv
from sgrequests import SgRequests
from sglogging import sglog
import json
from sgzip.dynamic import DynamicZipSearch, SearchableCountries
import lxml.html

website = "farmfoods.co.uk"
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
    search = DynamicZipSearch(country_codes=[SearchableCountries.BRITAIN])

    for zipcode in search:
        log.info(f"{zipcode} | remaining: {search.items_remaining()}")

        search_url = "https://www.farmfoods.co.uk/includes/store_finder.php?term={}"
        stores_req = session.get(search_url.format(zipcode), headers=headers)
        if "branches" in stores_req.text:
            stores = json.loads(stores_req.text)["branches"]
            for store in stores:
                page_url = "<MISSING>"

                locator_domain = website
                location_name = store["branch_name"]
                if location_name == "":
                    location_name = "<MISSING>"

                street_address = ""
                if store["address1"] is not None:
                    street_address = store["address1"]

                if store["address2"] is not None:
                    if len("".join(store["address2"]).strip()) > 0:
                        street_address = street_address + ", " + store["address2"]

                city = ""
                if store["address3"] is not None:
                    if len("".join(store["address3"]).strip()) > 0:
                        city = store["address3"]

                state = ""
                if store["address4"] is not None:
                    if len("".join(store["address4"]).strip()) > 0:
                        state = store["address4"]

                zip = ""
                if store["post_code"] is not None:
                    zip = store["post_code"]

                country_code = "<MISSING>"

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

                store_number = store["branch_code"]
                phone = "<MISSING>"

                location_type = "<MISSING>"

                latitude = store["latitude"]
                longitude = store["longitude"]

                search.found_location_at(latitude, longitude)

                if latitude == "" or latitude is None:
                    latitude = "<MISSING>"
                if longitude == "" or longitude is None:
                    longitude = "<MISSING>"

                hours_of_operation = ""
                store_sel = lxml.html.fromstring(store["popup"])
                hours = store_sel.xpath("text()")
                hours_list = []
                for hour in hours:
                    if len("".join(hour).strip()) > 0:
                        hours_list.append("".join(hour).strip())

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
                yield curr_list


def scrape():
    log.info("Started")
    data = fetch_data()
    write_output(data)
    log.info("Finished")


if __name__ == "__main__":
    scrape()
