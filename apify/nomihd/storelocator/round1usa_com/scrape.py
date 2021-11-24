# -*- coding: utf-8 -*-
import csv
from sgrequests import SgRequests
from sglogging import sglog
import json
import us
from sgscrape import sgpostal as parser

website = "round1usa.com"
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
                "raw_address",
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

    search_url = "https://api2.storepoint.co/v1/16026f2c5ac3c7/locations"
    stores_req = session.get(search_url, headers=headers)
    if json.loads(stores_req.text)["success"] is True:
        stores = json.loads(stores_req.text)["results"]["locations"]

        for store in stores:
            page_url = "https://round1usa.com/locations"
            locator_domain = website
            location_name = store["name"].replace("<br>", "").strip()
            if location_name == "":
                location_name = "<MISSING>"

            raw_address = store["streetaddress"]
            formatted_addr = parser.parse_address_usa(raw_address)
            street_address = formatted_addr.street_address_1
            if formatted_addr.street_address_2:
                street_address = street_address + ", " + formatted_addr.street_address_2

            city = formatted_addr.city
            state = formatted_addr.state
            zip = formatted_addr.postcode

            country_code = "<MISSING>"
            if us.states.lookup(state):
                country_code = "US"

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
            if "(" not in phone:
                phone = "<MISSING>"

            if "Temporarily Closed" in location_name:
                location_type = "Temporarily Closed"
            elif "Coming Soon" in location_name:
                location_type = "Coming Soon"
            else:
                location_type = "<MISSING>"

            hours_of_operation = ""
            hours_list = []
            if len(store["monday"]) > 0:
                hours_list.append("monday:" + store["monday"])
            else:
                hours_list.append("monday:" + "Closed")
            if len(store["tuesday"]) > 0:
                hours_list.append("tuesday:" + store["tuesday"])
            else:
                hours_list.append("tuesday:" + "Closed")
            if len(store["wednesday"]) > 0:
                hours_list.append("wednesday:" + store["wednesday"])
            else:
                hours_list.append("wednesday:" + "Closed")
            if len(store["thursday"]) > 0:
                hours_list.append("thursday:" + store["thursday"])
            else:
                hours_list.append("thursday:" + "Closed")
            if len(store["friday"]) > 0:
                hours_list.append("friday:" + store["friday"])
            else:
                hours_list.append("friday:" + "Closed")
            if len(store["saturday"]) > 0:
                hours_list.append("saturday:" + store["saturday"])
            else:
                hours_list.append("saturday:" + "Closed")
            if len(store["sunday"]) > 0:
                hours_list.append("sunday:" + store["sunday"])
            else:
                hours_list.append("sunday:" + "Closed")

            hours_of_operation = (
                "; ".join(hours_list)
                .strip()
                .replace("<br>", "")
                .replace("&nbsp", "")
                .replace(" ;", ";")
                .replace(":;", ":")
            )
            latitude = store["loc_lat"]
            longitude = store["loc_long"]

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
                raw_address,
            ]
            loc_list.append(curr_list)
    else:
        log.error("Something wrong with the response SUCCESS value")
        # break
    return loc_list


def scrape():
    log.info("Started")
    data = fetch_data()
    write_output(data)
    log.info("Finished")


if __name__ == "__main__":
    scrape()
