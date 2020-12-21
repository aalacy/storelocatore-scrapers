# -*- coding: utf-8 -*-
import csv
from sgrequests import SgRequests
from sglogging import sglog
import json
from bs4 import BeautifulSoup as BS

website = "goodfeet.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()

headers = {
    "Connection": "keep-alive",
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "X-Requested-With": "XMLHttpRequest",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36",
    "Content-Type": "application/json; charset=UTF-8",
    "Origin": "https://www.goodfeet.com",
    "Sec-Fetch-Site": "same-origin",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Dest": "empty",
    "Referer": "https://www.goodfeet.com/locations",
    "Accept-Language": "en-US,en-GB;q=0.9,en;q=0.8",
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

    data = "{}"
    search_url = "https://www.goodfeet.com/GFWebService.asmx/GetStoresLocation"
    stores_req = session.post(search_url, data=data, headers=headers)
    store_ids = json.loads(
        str(stores_req.json()).replace("{'d': '", "").replace("'}", "")
    )
    for id in store_ids:
        data = {}
        data["StoreID"] = id[0]

        store_resp = session.post(
            "https://www.goodfeet.com/GFWebService.asmx/GetLocationByID",
            data=json.dumps(data),
            headers=headers,
        )
        store = json.loads(
            BS(
                str(store_resp.json())
                .replace("{'d': '", "")
                .replace("'}", "")
                .replace("\\u003c", "<")
                .replace("\\u003e", ">")
                .strip()
                .replace("\\u0027", "'")
                .replace("\\r", "")
                .strip()
                .replace("\\n", "")
                .strip()
                .replace("\\", " ")
                .strip(),
                "html.parser",
            ).getText()
        )[0]

        page_url = store[23]
        locator_domain = website
        location_name = "The Good Feet Store " + store[19]
        street_address = store[1]
        city = store[3]
        state = store[4]
        zip = store[5]
        country_code = store[6]
        if country_code == "USA":
            country_code = "US"
        elif country_code == "Canada":
            country_code = "CA"

        if street_address == "":
            street_address = "<MISSING>"

        if city == "":
            city = "<MISSING>"

        if state == "":
            state = "<MISSING>"

        if zip == "":
            zip = "<MISSING>"

        if country_code == "":
            country_code = "<MISSING>"

        store_number = store[0]
        phone = store[9]
        if "(" in phone:
            if len(phone.split("(")) == 3:
                phone = phone.rsplit("(", 1)[0].strip()

        location_type = "<MISSING>"
        hours_of_operation = (
            store[7]
            .replace("Appointments Required. Call for Same Day Availability.", "")
            .replace("Open for appointments only. ", "")
            .replace("Evening Hours by Appointment Only", "")
            .replace("Open 7 Days A Week! ", "")
            .strip()
        )
        hours_of_operation = hours_of_operation.strip()
        latitude = store[14]
        longitude = store[15]

        if latitude == "" or latitude == "0":
            latitude = "<MISSING>"
        if longitude == "" or longitude == "0":
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
        if country_code == "US" or country_code == "CA":
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
