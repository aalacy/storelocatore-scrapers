# -*- coding: utf-8 -*-
import csv
from sgrequests import SgRequests
from sglogging import sglog
import lxml.html
import json

website = "hsamuel.co.uk"
session = SgRequests()
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36",
    "Accept": "*/*",
    "X-Requested-With": "XMLHttpRequest",
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

    search_url = "https://www.hsamuel.co.uk/webstore/secure/viewAllStores.sdo"
    stores_req = session.get(search_url, headers=headers)
    stores_sel = lxml.html.fromstring(stores_req.text)
    stores = stores_sel.xpath(
        '//a[@class="viewStorDetails js-omnitureTag-storeNumber"]'
    )

    for store in stores:
        page_url = "https://www.hsamuel.co.uk" + "".join(store.xpath("@href")).strip()
        locator_domain = website
        log.info(page_url)

        store_req = session.get(page_url, headers=headers)
        store_sel = lxml.html.fromstring(store_req.text)
        json_list = store_sel.xpath('//script[@type="application/ld+json"]/text()')
        for js in json_list:
            if "localBusiness" in js:
                json_text = js
                store_json = json.loads(json_text)

                location_name = store_json["name"]
                if location_name == "":
                    location_name = "<MISSING>"

                street_address = store_json["address"]["streetAddress"]
                city = store_json["address"]["addressLocality"]
                state = "<MISSING>"
                zip = store_json["address"]["postalCode"]
                country_code = "".join(
                    store_sel.xpath(
                        '//meta[@property="business:contact_data:country_name"]/@content'
                    )
                ).strip()

                city_to_remove = ", " + city
                street_address = street_address.replace(city_to_remove, "").strip()
                if "," == street_address[-1]:
                    street_address = street_address[:-1]

                if country_code == "" or country_code is None:
                    country_code = "<MISSING>"
                if street_address == "":
                    street_address = "<MISSING>"

                if city == "":
                    city = "<MISSING>"

                if state == "":
                    state = "<MISSING>"

                if zip == "":
                    zip = "<MISSING>"

                store_number = "".join(store.xpath("@data-store-number")).strip()
                if store_number == "":
                    store_number = "<MISSING>"

                phone = store_json["telephone"].strip()

                location_type = "<MISSING>"

                hours_of_operation = ""
                hours_of_operation = "; ".join(store_json["openingHours"]).strip()

                if hours_of_operation == "":
                    hours_of_operation = "<MISSING>"

                latitude = "".join(
                    store_sel.xpath(
                        '//meta[@property="place:location:latitude"]/@content'
                    )
                ).strip()
                longitude = "".join(
                    store_sel.xpath(
                        '//meta[@property="place:location:longitude"]/@content'
                    )
                ).strip()

                if latitude == "":
                    latitude = "<MISSING>"
                if longitude == "":
                    longitude = "<MISSING>"

                if phone == "":
                    phone = "<MISSING>"

                if country_code != "Republic of Ireland":
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
