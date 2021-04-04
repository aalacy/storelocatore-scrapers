# -*- coding: utf-8 -*-
import csv
from sgrequests import SgRequests
from sglogging import sglog
import json
import us
import lxml.html

website = "cumberlandfarms.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
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

    stores_resp = session.get(
        "https://www.cumberlandfarms.com/storedata/getstoredatabylocation",
        headers=headers,
    )
    stores_json = json.loads(stores_resp.text)
    for store in stores_json:
        if "StoreId" in store:
            store_number = store["StoreId"]
            page_url = "https://www.cumberlandfarms.com" + store["Url"]
            location_name = "Cumber Land Farms"
            street_address = store["Address"]
            if street_address == "":
                street_address = "<MISSING>"

            city = store["City"]
            state = store["State"]

            zip = store["Zip"]

            latitude = store["Latitude"]
            longitude = store["Longitude"]

            phone = store["Phone"]
            if phone == "":
                phone = "<MISSING>"

            if us.states.lookup(state):
                country_code = "US"

            if country_code == "":
                country_code = "<MISSING>"

            hours_of_operation = store["Hours"]
            s_req = session.get(page_url, headers=headers)
            store_sel = lxml.html.fromstring(s_req.text)
            location_type = "".join(
                store_sel.xpath(
                    '//div[@class="store-detail__store-card span-one-third"]'
                    "/@data-store"
                )
            ).strip()
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
    return loc_list


def scrape():
    log.info("Started")
    data = fetch_data()
    write_output(data)
    log.info("Finished")


if __name__ == "__main__":
    scrape()
