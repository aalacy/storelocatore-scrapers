# -*- coding: utf-8 -*-
import csv
from sgrequests import SgRequests
from sglogging import sglog
import json
import us

website = "desertsuntanning.com"
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

    search_url = "https://ds.atomicinfotech.com/api.php/storelookup/liststores"
    stores_req = session.get(search_url, headers=headers)
    stores = json.loads(stores_req.text)

    for key in stores.keys():
        if stores[key]["StoreName"] != "Corporate":
            page_url = (
                "https://desertsuntanning.com/locations?location="
                + stores[key]["StoreName"]
            )
            locator_domain = website
            location_name = stores[key]["StoreName"]
            if location_name == "":
                location_name = "<MISSING>"

            street_address = stores[key]["Address"]
            city = stores[key]["City"]
            state = stores[key]["State"]
            zip = stores[key]["Zip"]
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

            store_number = str(stores[key]["StoreNum"])
            phone = stores[key]["Phone"]

            location_type = stores[key]["Closed"]
            if location_type == "" or location_type is None:
                location_type = "<MISSING>"

            hours_of_operation = ""
            if stores[key]["Hours"] is not None:
                if len(stores[key]["Hours"]) > 0:
                    hours_of_operation = (
                        hours_of_operation + "Monday - Friday:" + stores[key]["Hours"]
                    )

            if stores[key]["Hours2"] is not None:
                if len(stores[key]["Hours2"]) > 0:
                    hours_of_operation = (
                        hours_of_operation + "Saturday:" + stores[key]["Hours2"]
                    )

            if stores[key]["Hours3"] is not None:
                if len(stores[key]["Hours3"]) > 0:
                    hours_of_operation = (
                        hours_of_operation + "Sunday:" + stores[key]["Hours3"]
                    )

            latitude = stores[key]["Latitude"]
            longitude = stores[key]["Longitude"]

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

    return loc_list


def scrape():
    log.info("Started")
    data = fetch_data()
    write_output(data)
    log.info("Finished")


if __name__ == "__main__":
    scrape()
