# -*- coding: utf-8 -*-
import csv
from sgrequests import SgRequests
from sglogging import sglog
import lxml.html
import json

website = "headmasters.com"
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

    search_url = "https://www.headmasters.com/wp-json/salon/list.json"
    stores_req = session.get(search_url, headers=headers)
    stores = json.loads(stores_req.text)
    for store in stores:
        location_name = store["name"]
        locator_domain = website
        page_url = store["url"]
        latitude = store["lat"]
        longitude = store["lng"]
        store_number = store["id"]
        log.info(page_url)
        store_req = session.get(page_url, headers=headers)
        store_sel = lxml.html.fromstring(store_req.text)
        json_list = store_sel.xpath('//script[@type="application/ld+json"]/text()')
        for js in json_list:
            if "OpeningHoursSpecification" in js:
                store_json = json.loads(js)

                location_type = "<MISSING>"

                street_address = store_json["address"]["streetAddress"]
                city_state = store_json["address"]["addressLocality"]
                city = ""
                state = "<MISSING>"
                if "," in city_state:
                    city = city_state.split(",")[0].strip()
                else:
                    city = city_state

                zip = store_json["address"]["postalCode"]
                phone = store_json["telephone"].replace("TEL", "").strip()
                days = store_sel.xpath('//span[@class="day__label"]/text()')
                time = store_sel.xpath('//span[@class="day__hours"]/text()')
                hours_list = []
                for index in range(0, len(days)):
                    if len("".join(time[index]).strip()) > 0:
                        hours_list.append(
                            "".join(days[index]).strip() + "".join(time[index]).strip()
                        )

                hours_of_operation = "; ".join(hours_list).strip()

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

                if hours_of_operation == "":
                    hours_of_operation = "<MISSING>"

                if location_type == "":
                    location_type = "<MISSING>"

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
