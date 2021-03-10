# -*- coding: utf-8 -*-
import csv
from sgrequests import SgRequests
from sglogging import sglog
import json
import lxml.html

website = "ryerson.com"
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

    urls = [
        "https://www.ryerson.com/en/locations/unitedstates",
        "https://www.ryerson.com/en/locations/canada",
    ]

    for url in urls:
        search_url = url
        stores_req = session.get(search_url, headers=headers)
        stores = json.loads(
            stores_req.text.split("var plantInfo = ")[1].strip().split("];")[0].strip()
            + "]"
        )

        for store in stores:
            page_url = "https://www.ryerson.com" + store["SCURL"]
            if "unitedstates" in page_url or "canada" in page_url:
                locator_domain = website
                location_name = store["PlantPublicName"]
                if location_name == "":
                    location_name = "<MISSING>"

                street_address = store["PlantStreet"]
                city = store["PlantCity"]
                state = store["PlantState"]
                zip = store["ZipCode"]

                country_code = "<MISSING>"
                if "unitedstates" in page_url:
                    country_code = "US"
                elif "canada" in page_url:
                    country_code = "CA"

                if street_address == "" or street_address is None:
                    street_address = "<MISSING>"

                if city == "" or city is None:
                    city = "<MISSING>"

                if state == "" or state is None:
                    state = "<MISSING>"

                if zip == "" or zip is None:
                    zip = "<MISSING>"

                store_number = str(store["Id"])
                phone = store["MainPhone"]

                location_type = "<MISSING>"
                hours_of_operation = "<MISSING>"

                latitude = store["lat"]
                longitude = store["lon"]

                if latitude == "" or latitude is None:
                    latitude = "<MISSING>"
                if longitude == "" or longitude is None:
                    longitude = "<MISSING>"

                if hours_of_operation == "":
                    hours_of_operation = "<MISSING>"

                if phone == "" or phone is None:
                    store_req = session.get(page_url, headers=headers)
                    store_sel = lxml.html.fromstring(store_req.text)
                    phone = "".join(
                        store_sel.xpath('//div[@itemprop="telephone"]/text()')
                    ).strip()
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

        # break
    return loc_list


def scrape():
    log.info("Started")
    data = fetch_data()
    write_output(data)
    log.info("Finished")


if __name__ == "__main__":
    scrape()
