# -*- coding: utf-8 -*-
import csv
from sgrequests import SgRequests
from sglogging import sglog
import lxml.html
import json

website = "praxair.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()

headers = {
    "accept": "application/json, text/plain, */*",
    "accept-encoding": "gzip, deflate, br",
    "accept-language": "en-US,en-GB;q=0.9,en;q=0.8",
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-origin",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/86.0.4240.198 Safari/537.36",
    "x-requested-with": "XMLHttpRequest",
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

    stores_req = session.get("https://www.praxairusa.com/stores", headers=headers)
    stores_sel = lxml.html.fromstring(stores_req.text)

    token = "".join(
        stores_sel.xpath(
            '//eco-widget-directive[@widget-name="util-scroll-to-top"]'
            "/@eco-request-verification-token-directive"
        )
    ).strip()

    headers["sc-requestverificationtoken"] = token
    stores_req = session.get(
        "https://www.praxairusa.com/ECO/Services/scStoreLocatorController"
        "/GetStoreLocatorList?distance=10000&position=30.19026900000001"
        "&position=-95.58724699999999&sc_cntrl_id=ctl00-PublicWrapper-C002",
        headers=headers,
    )
    stores = json.loads(stores_req.text)["storeLocatorList"]
    for store in stores:
        locator_domain = website
        page_url = store["DetailUrl"]
        location_name = store["CompanyName"]
        street_address = store["Address"]["Street"]
        city = store["Address"]["City"]
        state = store["Address"]["State"]
        zip = store["Address"]["Zip"]
        country_code = store["Address"]["CountryCode"]
        store_number = store["JDEBranchNumber"]
        if store_number == "XXX":
            store_number = "<MISSING>"

        phone = store["Phone"]
        location_type = ""
        latitude = store["Address"]["Latitude"]
        longitude = store["Address"]["Longitude"]
        hours_of_operation = ""
        hours_dict = store["StoreHours"]
        weekdays = [
            "Monday",
            "Tuesday",
            "Wednesday",
            "Thursday",
            "Friday",
            "Saturday",
            "Sunday",
        ]
        for day, hour in hours_dict.items():
            if day in weekdays:
                hours_of_operation = hours_of_operation + day + ": " + hour + " "
        if location_type == "":
            location_type = "<MISSING>"
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
