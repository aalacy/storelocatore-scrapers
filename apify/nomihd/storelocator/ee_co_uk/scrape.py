# -*- coding: utf-8 -*-
import csv
from sgrequests import SgRequests
from sglogging import sglog
import json
import lxml.html

website = "ee_co.uk"
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

    search_url = "https://ee.co.uk/bin/eestore/storepage.json"
    stores_req = session.get(search_url, headers=headers)
    stores = json.loads(stores_req.text)["storesJson"]

    for store in stores:
        page_url = (
            "https://ee.co.uk"
            + store["path"].replace("/content/ee-web/en_GB", "").strip()
        )

        log.info(page_url)
        store_req = session.get(page_url, headers=headers)
        store_sel = lxml.html.fromstring(store_req.text)
        store_json = json.loads(
            "".join(
                store_sel.xpath('//script[@type="application/ld+json"]/text()')
            ).strip()
        )

        locator_domain = website
        location_name = store_json["brand"]
        if location_name == "":
            location_name = "<MISSING>"

        street_address = ""
        city = ""
        state = ""
        zip = ""
        country_code = ""

        try:
            street_address = store_json["address"]["streetAddress"].strip()
        except:
            pass
        try:
            city = store_json["address"]["addressLocality"].strip()
        except:
            pass
        try:
            state = store_json["address"]["addressRegion"].strip()
        except:
            pass
        try:
            zip = store_json["address"]["postalCode"].strip()
        except:
            pass
        try:
            country_code = store_json["address"]["addressCountry"].strip()
        except:
            pass

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

        store_number = store_json["branchCode"]
        phone = store_json["telephone"].strip()

        location_type = store_json["@type"]

        latitude = store_json["geo"]["latitude"]
        longitude = store_json["geo"]["longitude"]

        if latitude == "" or latitude is None:
            latitude = "<MISSING>"
        if longitude == "" or longitude is None:
            longitude = "<MISSING>"

        hours_of_operation = ""
        hours = store_json["openingHoursSpecification"]
        hours_list = []
        for hour in hours:
            days = hour["dayOfWeek"]
            time = hour["opens"] + "-" + hour["closes"]
            for day in days:
                hours_list.append(day + ":" + time)

        hours_of_operation = "; ".join(hours_list).strip()

        if hours_of_operation == "":
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
