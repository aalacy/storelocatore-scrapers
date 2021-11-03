# -*- coding: utf-8 -*-
import csv
from sgrequests import SgRequests
from sglogging import sglog
import lxml.html
import us

website = "dierbergs.com"
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

    search_url = "https://www.dierbergs.com/MyDierbergs/Locations"
    stores_req = session.get(search_url, headers=headers)
    stores_sel = lxml.html.fromstring(stores_req.text)
    stores = stores_sel.xpath('//div[@class="location-listing"]/div')
    for store in stores:
        page_url = (
            "https://www.dierbergs.com"
            + "".join(
                store.xpath(
                    'div[@class="location-listing-item-store col-xs-7"]/h4/a/@href'
                )
            ).strip()
        )
        locator_domain = website

        location_name = "".join(
            store.xpath(
                'div[@class="location-listing-item-store col-xs-7"]/h4/a/strong/text()'
            )
        ).strip()
        if location_name == "":
            location_name = "<MISSING>"

        street_address = "".join(
            store.xpath(
                'div[@class="location-listing-item-store col-xs-7"]/span[@class="address"]/text()'
            )
        ).strip()
        city = "".join(
            store.xpath(
                'div[@class="location-listing-item-store col-xs-7"]/span[@class="city"]/text()'
            )
        ).strip()

        state = "".join(
            store.xpath(
                'div[@class="location-listing-item-store col-xs-7"]/span[@class="state"]/text()'
            )
        ).strip()
        zip = "".join(
            store.xpath(
                'div[@class="location-listing-item-store col-xs-7"]/span[@class="zip"]/text()'
            )
        ).strip()

        country_code = "<MISSING>"
        if us.states.lookup(state):
            country_code = "US"

        if street_address == "":
            street_address = "<MISSING>"

        if city == "":
            city = "<MISSING>"

        if state == "":
            state = "<MISSING>"

        if zip == "":
            zip = "<MISSING>"

        store_number = "<MISSING>"
        phone = "".join(
            store.xpath(
                'div[@class="location-listing-item-store col-xs-7"]/span[@class="phone"]/a[1]/text()'
            )
        ).strip()

        location_type = "<MISSING>"
        hours_of_operation = "".join(
            store.xpath(
                'div[@class="location-listing-item-store col-xs-7"]/span[@class="pharmacyHours"]/text()[1]'
            )
        ).strip()

        latitude = "".join(store.xpath("@data-lat"))
        longitude = "".join(store.xpath("@data-lon"))
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

    return loc_list


def scrape():
    log.info("Started")
    data = fetch_data()
    write_output(data)
    log.info("Finished")


if __name__ == "__main__":
    scrape()
