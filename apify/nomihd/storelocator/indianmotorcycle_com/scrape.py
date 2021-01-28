# -*- coding: utf-8 -*-
import csv
from sgrequests import SgRequests
from sglogging import sglog
import json

website = "indianmotorcycle.com"
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

    loc_list = []
    locator_domain = website
    page_url = (
        "https://etc.polaris.com/api/v1/dealers?lat=37.0902&lon=95.7129"
        "&recordCount=1000&geoFenceCountry=&plc=ind&distanceType=mi"
        "&distanceToLook=200000&virtualTerritorySearch=false"
    )
    locations_resp = session.get(
        page_url,
        headers=headers,
    )
    stores = json.loads(locations_resp.text)
    for store_json in stores:
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

        location_name = store_json["businessName"]
        street_address = store_json["address1"]
        city = store_json["city"]
        state = store_json["region"]
        if state == "":
            state = "<MISSING>"

        zip = store_json["postalCode"]
        if zip == "":
            zip = "<MISSING>"

        if location_type == "":
            location_type = "<MISSING>"

        latitude = store_json["latitude"]
        longitude = store_json["longitude"]

        country_code = store_json["country"]
        if country_code == "":
            country_code = "<MISSING>"

        store_number = store_json["dealerId"]
        phone = store_json["phone"]

        if not phone:
            phone = "<MISSING>"

        hours = store_json["storeHours"]
        if hours is not None:
            for hour in hours:
                if hour["openTime"] == "" and hour["closeTime"] == "":
                    hours_of_operation = (
                        hours_of_operation + hour["dayOfWeek"] + ":" + "Closed" + " "
                    )
                else:
                    hours_of_operation = (
                        hours_of_operation
                        + hour["dayOfWeek"]
                        + ":"
                        + hour["openTime"]
                        + "-"
                        + hour["closeTime"]
                        + " "
                    )

        if hours_of_operation == "":
            hours_of_operation = "<MISSING>"

        if country_code == "US" or country_code == "CA":
            page_url = store_json["webSite"]
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
