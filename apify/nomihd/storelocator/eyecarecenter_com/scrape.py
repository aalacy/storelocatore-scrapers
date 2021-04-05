# -*- coding: utf-8 -*-
import csv
from sgrequests import SgRequests
from sglogging import sglog
import json
from sgzip.dynamic import DynamicGeoSearch, SearchableCountries
import lxml.html

website = "eyecarecenter.com"
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
    search = DynamicGeoSearch(
        country_codes=[SearchableCountries.USA], max_radius_miles=50
    )

    for lat, long in search:
        log.info(f"{(lat, long)} | remaining: {search.items_remaining()}")

        search_url = "https://www.eyecarecenter.com/wp-json/352inc/v1/locations/coordinates?lat={}&lng={}"
        search_url = search_url.format(lat, long)
        stores_req = session.get(search_url, headers=headers)
        if "permalink" in stores_req.text:
            stores = json.loads(stores_req.text)
            for store in stores:
                page_url = store["permalink"]
                log.info(page_url)
                store_req = session.get(page_url, headers=headers)
                store_sel = lxml.html.fromstring(store_req.text)
                json_list = store_sel.xpath(
                    '//script[@type="application/ld+json"]/text()'
                )
                store_json = None
                for js in json_list:
                    if "latitude" in js:
                        store_json = json.loads(js)
                        break

                locator_domain = website
                location_name = store_json["name"]
                if location_name == "":
                    location_name = "<MISSING>"

                street_address = store_json["address"]["streetAddress"]
                city = store_json["address"]["addressLocality"]
                state = store_json["address"]["addressRegion"]
                zip = store_json["address"]["postalCode"]
                country_code = store_json["address"]["addressCountry"]

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

                store_number = "<MISSING>"
                phone = store_json["telephone"]

                location_type = "<MISSING>"

                latitude = store_json["geo"]["latitude"]
                longitude = store_json["geo"]["longitude"]

                search.found_location_at(latitude, longitude)

                if latitude == "" or latitude is None:
                    latitude = "<MISSING>"
                if longitude == "" or longitude is None:
                    longitude = "<MISSING>"

                hours_of_operation = ""
                hours = store_json["openingHoursSpecification"]
                hours_list = []
                for hour in hours:
                    day = hour["dayOfWeek"]
                    time = hour["opens"] + "-" + hour["closes"]
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
                yield curr_list



def scrape():
    log.info("Started")
    data = fetch_data()
    write_output(data)
    log.info("Finished")


if __name__ == "__main__":
    scrape()
