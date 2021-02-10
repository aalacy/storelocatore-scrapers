# -*- coding: utf-8 -*-
import csv
from sgrequests import SgRequests
from sglogging import sglog
import lxml.html
import json

website = "waterstones.co.uk"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "authority": "www.waterstones.com",
    "sec-ch-ua": '"Chromium";v="88", "Google Chrome";v="88", ";Not A Brand";v="99"',
    "accept": "application/json, text/javascript, */*; q=0.01",
    "x-newrelic-id": "VQUHVlRRDxABUVlbAQUPXg==",
    "x-requested-with": "XMLHttpRequest",
    "sec-ch-ua-mobile": "?0",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.104 Safari/537.36",
    "sec-fetch-site": "same-origin",
    "sec-fetch-mode": "cors",
    "sec-fetch-dest": "empty",
    "referer": "https://www.waterstones.com/bookshops",
    "accept-language": "en-US,en;q=0.9",
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

    search_url = "https://www.waterstones.com/bookshops/findall"
    stores_req = session.get(search_url, headers=headers)

    stores = json.loads(stores_req.text)["data"]
    for store in stores:
        locator_domain = website
        location_name = store["name"]
        page_url = "https://www.waterstones.com" + store["url"]
        latitude = store["latitude"]
        longitude = store["longitude"]
        store_number = store["id"]
        street_address = store["address_1"]
        if store["address_2"] is not None and len(store["address_2"]) > 0:
            street_address = street_address + ", " + store["address_2"]

        city = store["address_3"]
        zip = store["postcode"]
        country_code = "GB"
        state = "<MISSING>"
        phone = store["telephone"]
        location_type = store["closed_message"]
        hours_of_operation = "<MISSING>"

        if store_number == "":
            store_number = "<MISSING>"

        if location_name == "":
            location_name = "<MISSING>"

        country_code = "GB"

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

        if phone == "" or phone is None:
            phone = "<MISSING>"

        if latitude == "" or latitude is None:
            latitude = "<MISSING>"
        if longitude == "" or longitude is None:
            longitude = "<MISSING>"

        if location_type == "":
            location_type = "<MISSING>"
            log.info(page_url)
            store_req = session.get(page_url)
            store_sel = lxml.html.fromstring(store_req.text)
            hours = store_sel.xpath('//div[@class="opening-times"]/div')
            hours_list = []
            for hour in hours:
                day = "".join(hour.xpath('.//div[@class="day"]/text()')).strip()
                time = "".join(hour.xpath('.//div[@class="times"]/text()')).strip()

                if len(time) > 0:
                    day = day.split(" ")[0].strip()
                    hours_list.append(day + ":" + time)

            hours_of_operation = "; ".join(hours_list).strip()

        if hours_of_operation == "":
            hours_of_operation = "<MISSING>"

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
