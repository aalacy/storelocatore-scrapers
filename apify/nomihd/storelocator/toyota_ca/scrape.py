# -*- coding: utf-8 -*-
import csv
from sgrequests import SgRequests
from sglogging import sglog
import json

website = "toyota.ca"
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

    search_url = "https://www.toyota.ca/toyota/data/dealer/.json"
    stores_req = session.get(search_url, headers=headers)
    stores = json.loads(stores_req.text)["dealers"]

    for key in stores.keys():
        page_url = "https://www.toyota.ca/toyota/en/dealer/" + stores[key]["code"]
        locator_domain = website
        location_name = stores[key]["name"]["en"]
        if location_name == "":
            location_name = "<MISSING>"

        street_address = stores[key]["address"]["streetAddress"]
        city = stores[key]["address"]["city"]
        state = stores[key]["address"]["province"]
        zip = stores[key]["address"]["postalCode"]

        country_code = "CA"
        if street_address == "" or street_address is None:
            street_address = "<MISSING>"

        if city == "" or city is None:
            city = "<MISSING>"

        if state == "" or state is None:
            state = "<MISSING>"

        if zip == "" or zip is None:
            zip = "<MISSING>"

        store_number = str(stores[key]["code"])
        temp_phone = stores[key]["phoneNumbers"][0]["CompleteNumber"]["$"]
        phone = "(" + temp_phone[:3] + ") " + temp_phone[3:6] + "-" + temp_phone[6:]
        location_type = "<MISSING>"
        hours_list = []
        departments = stores[key]["departments"]
        for dep in departments:
            if "hours" in dep:
                hours = dep["hours"]
                hours_list = []
                hours_of_operation = ""
                for hour in hours:
                    day = ""
                    if "toDay" in hour:
                        day = hour["fromDay"]["en"] + "-" + hour["toDay"]["en"]
                    else:
                        day = hour["fromDay"]["en"]

                    time = hour["startTime"]["en"] + "-" + hour["endTime"]["en"]
                    hours_list.append(day + ":" + time)
                break

        hours_of_operation = "; ".join(hours_list).strip()

        latitude = stores[key]["location"]["lat"]
        longitude = stores[key]["location"]["lng"]

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

        # break
    return loc_list


def scrape():
    log.info("Started")
    data = fetch_data()
    write_output(data)
    log.info("Finished")


if __name__ == "__main__":
    scrape()
