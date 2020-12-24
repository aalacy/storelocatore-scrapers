# -*- coding: utf-8 -*-
import csv
from sgrequests import SgRequests
from sglogging import sglog
import json
import us
import lxml.html

website = "brookshirebrothers.com"
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

    search_url = "https://brookshirebrothers.force.com/QuestionOrComments"
    stores_req = session.get(search_url, headers=headers)
    stores_sel = lxml.html.fromstring(stores_req.text)
    store_list = stores_sel.xpath('//select[@class="smallText"]/option/text()')
    for index in range(1, len(store_list)):
        zip = (
            store_list[index]
            .split("--")[0]
            .strip()
            .split(",")[1]
            .strip()
            .split(" ")[-1]
        )
        url = (
            "https://www.brookshirebrothers.com/"
            "store-locator-results/{}/store-locator"
        )

        stores_req = session.get(url.format(zip), headers=headers)
        stores = json.loads(stores_req.text)["stores"]
        for store in stores:
            page_url = "https://www.brookshirebrothers.com" + store["link"]
            locator_domain = website
            location_name = store["the_title"]
            if location_name == "":
                location_name = "<MISSING>"

            street_address = store["address"]
            city = store["city"]
            state = store["state"]
            zip = store["zip"]

            if street_address == "":
                street_address = "<MISSING>"

            if city == "":
                city = "<MISSING>"

            if state == "":
                state = "<MISSING>"

            if zip == "":
                zip = "<MISSING>"

            country_code = "<MISSING>"
            if us.states.lookup(state):
                country_code = "US"

            store_number = store["number"]
            if store_number == "":
                store_number = "<MISSING>"

            phone = store["phone"]

            location_type = "<MISSING>"
            hours_of_operation = store["hours"]

            latitude = store["lat"]
            longitude = store["lng"]

            if latitude == "":
                latitude = "<MISSING>"
            if longitude == "":
                longitude = "<MISSING>"

            if hours_of_operation is None or hours_of_operation == "":
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

    return loc_list


def scrape():
    log.info("Started")
    data = fetch_data()
    write_output(data)
    log.info("Finished")


if __name__ == "__main__":
    scrape()
