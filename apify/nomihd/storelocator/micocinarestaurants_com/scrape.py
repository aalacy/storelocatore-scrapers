# -*- coding: utf-8 -*-
import csv
from sgrequests import SgRequests
from sglogging import sglog
import json
import us

website = "micocinarestaurants.com"
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

    search_url = "https://www.micocina.com/wp-admin/admin-ajax.php"

    data = {
        "action": "get_all_stores",
        "lat": "",
        "lng": "",
    }

    stores_req = session.post(search_url, data=data, headers=headers)
    stores = json.loads(stores_req.text)

    for key in stores.keys():
        latitude = stores[key]["lat"]
        longitude = stores[key]["lng"]
        page_url = stores[key]["gu"]

        locator_domain = website
        location_name = stores[key]["na"]
        if location_name == "":
            location_name = "<MISSING>"

        street_address = stores[key]["st"]
        city = stores[key]["ct"]
        state = stores[key]["rg"]
        zip = stores[key]["zp"]
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

        store_number = str(stores[key]["ID"])
        location_type = "<MISSING>"

        phone = stores[key]["te"]
        hours = stores[key]["op"]
        hours_of_operation = ""
        if len(hours["0"].strip()) > 0:
            hours_of_operation = (
                hours_of_operation + "Monday:" + hours["0"] + "-" + hours["1"] + ";"
            )

        if len(hours["2"].strip()) > 0:
            hours_of_operation = (
                hours_of_operation + "Tuesday:" + hours["2"] + "-" + hours["3"] + ";"
            )

        if len(hours["4"].strip()) > 0:
            hours_of_operation = (
                hours_of_operation + "Wednesday:" + hours["4"] + "-" + hours["5"] + ";"
            )

        if len(hours["6"].strip()) > 0:
            hours_of_operation = (
                hours_of_operation + "Thursday:" + hours["6"] + "-" + hours["7"] + ";"
            )
        if len(hours["8"].strip()) > 0:
            hours_of_operation = (
                hours_of_operation + "Friday:" + hours["8"] + "-" + hours["9"] + ";"
            )

        if len(hours["10"].strip()) > 0:
            hours_of_operation = (
                hours_of_operation + "Saturday:" + hours["10"] + "-" + hours["11"] + ";"
            )

        if len(hours["12"].strip()) > 0:
            hours_of_operation = (
                hours_of_operation + "Sunday:" + hours["12"] + "-" + hours["13"]
            )

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
