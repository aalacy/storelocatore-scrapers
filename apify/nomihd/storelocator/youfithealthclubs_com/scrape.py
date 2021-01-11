# -*- coding: utf-8 -*-
import csv
from sgrequests import SgRequests
from sglogging import sglog
import json
import us

website = "youfithealthclubs.com"
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

    search_url = (
        "https://youfit.api.omnimerse.com/youfit/youfit-geolocation-service/v1/clubs"
    )
    stores_req = session.get(search_url, headers=headers)
    stores = json.loads(stores_req.text)["Clubs"]
    for store in stores:
        if store["Status"] != "Inactive":
            locator_domain = website
            location_name = store["Club_Name"]
            if location_name == "":
                location_name = "<MISSING>"

            street_address = store["Address_1"]
            city = store["City"]
            state = store["State"]
            zip = str(store["Zip_Code"])
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

            store_number = str(store["ABC_Club_ID"])
            page_url = (
                "https://youfit.com/gym/" + store["URL_Name"] + "-" + store_number
            )

            phone = store["Phone_Number"]

            location_type = "<MISSING>"
            hours_of_operation = (
                "Mon:" + store["Location_Hours_Monday"] + " "
                "Tue:" + store["Location_Hours_Tuesday"] + " "
                "Wed:" + store["Location_Hours_Wednesday"] + " "
                "Thu:" + store["Location_Hours_Thursday"] + " "
                "Fri:" + store["Location_Hours_Friday"] + " "
                "Sat:" + store["Location_Hours_Saturday"] + " "
                "Sun:" + store["Location_Hours_Sunday"]
            )

            if hours_of_operation == "" or hours_of_operation is None:
                hours_of_operation = "<MISSING>"

            latitude = store["Latitude"]
            longitude = store["Longitude"]

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
