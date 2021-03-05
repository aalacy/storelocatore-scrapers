# -*- coding: utf-8 -*-
import csv
from sgrequests import SgRequests
from sglogging import sglog
import lxml.html
import json

website = "bareminerals.com"
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

    search_url = "https://stores.bareminerals.com/"
    states_req = session.get(search_url, headers=headers)
    states_sel = lxml.html.fromstring(states_req.text)
    states = states_sel.xpath('//div[@class="itemlist"]/a/@href')
    for state_url in states:
        cities_req = session.get(state_url, headers=headers)
        cities_sel = lxml.html.fromstring(cities_req.text)
        cities = cities_sel.xpath('//div[@class="itemlist"]/a/@href')
        for city_url in cities:
            stores_req = session.get(city_url, headers=headers)
            stores_sel = lxml.html.fromstring(stores_req.text)
            stores = stores_sel.xpath(
                '//li/a[contains(text(),"View Store Details")]/@href'
            )
            for store_url in stores:
                page_url = store_url
                store_req = session.get(page_url, headers=headers)
                store_sel = lxml.html.fromstring(store_req.text)

                store_json = None
                json_list = store_sel.xpath(
                    '//script[@type="application/ld+json"]/text()'
                )
                for js in json_list:
                    if '"@type":"HealthAndBeautyBusiness"' in js:
                        open("page_source.html", "w").write(
                            js.replace(
                                "//if applied, use the tmpl_var to retrieve the database value",
                                "",
                            )
                            .strip()
                            .replace('//"', '"')
                            .strip()
                            .split('"menu"')[0]
                            .strip()
                            + "}"
                        )
                        store_json = json.loads(
                            js.replace(
                                "//if applied, use the tmpl_var to retrieve the database value",
                                "",
                            )
                            .strip()
                            .replace('//"', '"')
                            .strip()
                            .split('"menu"')[0]
                            .strip()
                            + "}"
                        )

                locator_domain = website
                location_name = store_json["name"]
                if location_name == "":
                    location_name = "<MISSING>"

                street_address = store_json["address"]["streetAddress"]
                city = store_json["address"]["addressLocality"]
                state = store_json["address"]["addressRegion"]
                zip = store_json["address"]["postalCode"]

                country_code = store_json["address"]["addressCountry"]

                if street_address == "":
                    street_address = "<MISSING>"

                if city == "":
                    city = "<MISSING>"

                if state == "":
                    state = "<MISSING>"

                if zip == "":
                    zip = "<MISSING>"

                store_number = "<MISSING>"
                phone = store_json["telephone"]
                location_type = "<MISSING>"
                hours = store_json["openingHoursSpecification"]
                hours_of_operation = ""
                for hour in hours:
                    day = hour["dayOfWeek"][0]
                    time = hour["opens"] + "-" + hour["closes"]
                    hours_of_operation = hours_of_operation + day + ":" + time + " "

                hours_of_operation = hours_of_operation.strip()
                latitude = store_json["geo"]["latitude"]
                longitude = store_json["geo"]["longitude"]

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
        #         break
        #     break
        # break

    return loc_list


def scrape():
    log.info("Started")
    data = fetch_data()
    write_output(data)
    log.info("Finished")


if __name__ == "__main__":
    scrape()
