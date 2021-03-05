# -*- coding: utf-8 -*-
import csv
from sgrequests import SgRequests
from sglogging import sglog
import json
import us
import lxml.html

website = "superiorgrocers.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "authority": "superiorgrocers.com",
    "sec-ch-ua": '"Google Chrome";v="87", " Not;A Brand";v="99", "Chromium";v="87"',
    "accept": "application/json, text/javascript, */*; q=0.01",
    "x-requested-with": "XMLHttpRequest",
    "sec-ch-ua-mobile": "?0",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36",
    "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
    "origin": "https://superiorgrocers.com",
    "sec-fetch-site": "same-origin",
    "sec-fetch-mode": "cors",
    "sec-fetch-dest": "empty",
    "referer": "https://superiorgrocers.com/locations/",
    "accept-language": "en-US,en-GB;q=0.9,en;q=0.8",
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

    stores_req = session.get("https://superiorgrocers.com/locations/")
    stores_sel = lxml.html.fromstring(stores_req.text)
    locations = stores_sel.xpath('//div[contains(@class,"locationSide")]')
    hours_dict = {}
    for loc in locations:
        hours = (
            "".join(loc.xpath('.//div[contains(@id,"hours")]/text()'))
            .strip()
            .replace("Store Hours:", "")
            .strip()
        )
        slug = (
            "".join(loc.xpath('.//a[contains(text(),"More Info")]/@href'))
            .strip()
            .replace("/location/", "")
            .strip()
        )

        hours_dict[slug] = hours

    search_url = "https://superiorgrocers.com/locations/_ajax_map.php"
    data = {"myZip": "undefined", "lat": "undefined", "lng": "undefined"}

    stores_req = session.post(search_url, data=data, headers=headers)
    stores = json.loads(stores_req.text)

    for store in stores:
        page_url = "https://superiorgrocers.com/location/" + store["slug"]

        locator_domain = website
        location_name = store["name"]
        if location_name == "":
            location_name = "<MISSING>"

        street_address = store["address1"].strip()

        if len(store["address2"]) > 0:
            street_address = street_address + " " + store["address2"]

        city = store["city"].strip()
        state = store["state"].strip()
        zip = store["zip"].strip()
        country_code = ""
        if us.states.lookup(state):
            country_code = "US"

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

        store_number = store["ID"]
        phone = store["phone"].strip()

        location_type = "<MISSING>"

        latitude = store["lat"]
        longitude = store["lon"]

        if latitude == "" or latitude is None:
            latitude = "<MISSING>"
        if longitude == "" or longitude is None:
            longitude = "<MISSING>"

        hours_of_operation = ""

        if store["slug"] in hours_dict:
            hours_of_operation = hours_dict[store["slug"]]
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
