# -*- coding: utf-8 -*-
import csv
from sgrequests import SgRequests
from sglogging import sglog
import lxml.html

website = "capecodfive.com"
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

    search_url = "https://www.capecodfive.com/personal/locations"
    stores_req = session.get(search_url, headers=headers)
    stores_sel = lxml.html.fromstring(stores_req.text)
    stores = stores_sel.xpath('//div[@class="geolocation"]')

    for store in stores:
        page_url = (
            "https://www.capecodfive.com"
            + "".join(store.xpath('h2[@class="location-title"]/a/@href')).strip()
        )
        locator_domain = website
        location_name = "".join(
            store.xpath('h2[@class="location-title"]/a/text()')
        ).strip()
        if location_name == "":
            location_name = "<MISSING>"

        street_address = (
            "".join(
                store.xpath(
                    'div[@class="location-content"]//p[@class="address"]/span[@class="address-line1"]/text()'
                )
            )
            .strip()
            .replace("(also accessible from Tupper Rd)", "")
            .strip()
        )
        city = "".join(
            store.xpath(
                'div[@class="location-content"]//p[@class="address"]/span[@class="locality"]/text()'
            )
        ).strip()
        state = "".join(
            store.xpath(
                'div[@class="location-content"]//p[@class="address"]/span[@class="administrative-area"]/text()'
            )
        ).strip()
        zip = "".join(
            store.xpath(
                'div[@class="location-content"]//p[@class="address"]/span[@class="postal-code"]/text()'
            )
        ).strip()
        country_code = "".join(
            store.xpath(
                'div[@class="location-content"]//p[@class="address"]/span[@class="country"]/text()'
            )
        ).strip()

        if street_address == "":
            street_address = "<MISSING>"

        if city == "":
            city = "<MISSING>"

        if state == "":
            state = "<MISSING>"

        if zip == "":
            zip = "<MISSING>"

        store_number = "<MISSING>"
        phone = "".join(store.xpath('.//a[contains(@href,"tel:")]/text()')).strip()

        location_type = "<MISSING>"

        latitude = "".join(store.xpath("@data-lat")).strip()
        longitude = "".join(store.xpath("@data-lng")).strip()

        if latitude == "":
            latitude = "<MISSING>"
        if longitude == "":
            longitude = "<MISSING>"

        log.info(page_url)
        store_req = session.get(page_url, headers=headers)
        store_sel = lxml.html.fromstring(store_req.text)

        hours = store_sel.xpath('//span[@class="office-hours__item"]')

        hours_of_operation = ""
        hours_list = []
        for hour in hours:
            day = "".join(
                hour.xpath('span[@class="office-hours__item-label"]/text()')
            ).strip()
            time = "".join(
                hour.xpath('span[@class="office-hours__item-slots"]/text()')
            ).strip()
            hours_list.append(day + time)

        hours_of_operation = "; ".join(hours_list).strip()

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
