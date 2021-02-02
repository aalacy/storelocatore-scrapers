# -*- coding: utf-8 -*-
import csv
from sgselenium import SgChrome
from sglogging import sglog
import json
import us
from tenacity import retry, retry_if_exception_type

website = "fleetfarm.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)


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


@retry(stop=retry_if_exception_type())
def get_json(driver, page_url):
    driver.get(page_url)
    resp = None
    try:
        resp = (
            "{"
            + driver.page_source.split("KP_STORES = {")[1]
            .strip()
            .split("]};")[0]
            .strip()
            + "]}"
        )

    except:
        pass
    return resp


def fetch_data():
    # Your scraper here
    loc_list = []

    search_url = "https://www.fleetfarm.com/sitewide/storeLocator.jsp"

    with SgChrome() as driver:
        response = get_json(driver, search_url)
        stores = json.loads(response)["locations"]

        for store in stores:
            page_url = "https://www.fleetfarm.com" + store["redirectUrl"]

            locator_domain = website
            location_name = store["name"]
            if location_name == "":
                location_name = "<MISSING>"

            street_address = store["address"]
            city = store["city"]
            state = store["state"]
            zip = store["zip"]

            country_code = ""
            if us.states.lookup(state):
                country_code = "US"

            if country_code == "":
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

            store_number = store["locationId"]
            phone = store["phone"]

            location_type = "<MISSING>"

            latitude = store["lat"]
            longitude = store["lng"]

            if latitude == "" or latitude is None:
                latitude = "<MISSING>"
            if longitude == "" or longitude is None:
                longitude = "<MISSING>"

            hours_of_operation = store["serviceCenterHours"]

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

    return loc_list


def scrape():
    log.info("Started")
    data = fetch_data()
    write_output(data)
    log.info("Finished")


if __name__ == "__main__":
    scrape()
