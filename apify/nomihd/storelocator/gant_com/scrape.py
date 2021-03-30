# -*- coding: utf-8 -*-
import csv
from sgrequests import SgRequests
from sglogging import sglog

website = "gant.com"
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

    countries = session.get(
        "https://stores.gant.com/?controller=storelocator_default&action=getcountries",
        headers=headers,
    ).json()
    for country in countries:
        if (
            country == "canada"
            or country == "united kingdom"
            or country == "united states"
        ):
            cities = session.get(
                "https://stores.gant.com/?controller=storelocator_default&action=getcities&country="
                + country,
                headers=headers,
            ).json()
            for city in cities:
                stores = session.get(
                    "https://stores.gant.com/?controller=storelocator_default&action=getstoresfromcity&city="
                    + city,
                    headers=headers,
                ).json()

                for store in stores:
                    page_url = "<MISSING>"

                    locator_domain = website
                    location_name = store["storeName"]
                    if location_name == "":
                        location_name = "<MISSING>"

                    street_address = store["address"]["streetName"]
                    city = store["address"]["city"]
                    state = store["address"]["region"]
                    zip = store["address"]["postalCode"]

                    country_code = store["address"]["country"]

                    if street_address == "" or street_address is None:
                        street_address = "<MISSING>"

                    if city == "" or city is None:
                        city = "<MISSING>"

                    if state == "" or state is None:
                        state = "<MISSING>"

                    if zip == "" or zip is None:
                        zip = "<MISSING>"

                    store_number = str(store["storeId"])
                    phone = store["telephone"]

                    location_type = store["storeFormat"]
                    hours = store["openingHours"]
                    hours_list = []
                    for day in hours.keys():
                        start = hours[day]["from"]
                        end = hours[day]["to"]
                        if len(start) > 0 and len(end) > 0:
                            hours_list.append(day + ":" + start + "-" + end)

                    hours_of_operation = ";".join(hours_list).strip()

                    latitude = store["mapLocation"]["lat"]
                    longitude = store["mapLocation"]["long"]

                    if latitude == "" or latitude is None:
                        latitude = "<MISSING>"
                    if longitude == "" or longitude is None:
                        longitude = "<MISSING>"

                    if location_type == "" or location_type is None:
                        location_type = "<MISSING>"

                    if hours_of_operation == "" or hours_of_operation is None:
                        hours_of_operation = "<MISSING>"

                    if phone == "" or phone is None:
                        phone = "<MISSING>"

                    if country_code != "Ireland":
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
