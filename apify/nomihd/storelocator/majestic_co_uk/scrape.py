# -*- coding: utf-8 -*-
import csv
from sgrequests import SgRequests
from sglogging import sglog
import lxml.html
from sgscrape import sgpostal as parser

website = "majestic.co.uk"
domain = "https://www.majestic.co.uk"
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

    search_url = "https://www.majestic.co.uk/stores"
    home_req = session.get(search_url, headers=headers)
    home_sel = lxml.html.fromstring(home_req.text)
    regions = home_sel.xpath(
        '//div[@class="LinkButton t-link text-center mb-2 text-left content-wrapper"]/div/a/@href'
    )
    for region_url in regions:
        stores_req = session.get(domain + region_url, headers=headers)
        stores_sel = lxml.html.fromstring(stores_req.text)
        stores = stores_sel.xpath('//span[@class="store-list-buttons"]')
        for store in stores:
            locator_domain = website
            store_data = store.xpath('a[@class="d-inline-block view-on-map"]')[0]
            location_name = "".join(store_data.xpath("@data-name")).strip()
            page_url = domain + "".join(store_data.xpath("@data-id")).strip()
            latitude = "".join(store_data.xpath("@data-lat")).strip()
            longitude = "".join(store_data.xpath("@data-long")).strip()
            store_number = "<MISSING>"
            phone = "".join(store_data.xpath("@data-phone")).strip()

            log.info(page_url)

            store_req = session.get(page_url, headers=headers)
            store_sel = lxml.html.fromstring(store_req.text)
            location_type = "<MISSING>"
            raw_address = "".join(
                store_sel.xpath('//p[@class="store__address"]/text()')
            ).strip()

            formatted_addr = parser.parse_address_intl(raw_address)
            street_address = formatted_addr.street_address_1
            if formatted_addr.street_address_2:
                street_address = street_address + ", " + formatted_addr.street_address_2

            city = formatted_addr.city
            state = formatted_addr.state
            zip = formatted_addr.postcode

            if "temporarily closed" in store_req.text:
                location_type = "temporarily closed"

            hours = store_sel.xpath('//div[@class="store-time-line"]')
            hours_list = []
            for hour in hours:
                day = "".join(hour.xpath('span[@class="store-day"]/text()')).strip()
                time = "".join(
                    hour.xpath(
                        'span[@class="store-day"]/span//span[@class="store-time"]/text()'
                    )
                ).strip()
                if len(time) > 0 and "Bank Holidays" not in day:
                    hours_list.append(day + ":" + time)

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

    return loc_list


def scrape():
    log.info("Started")
    data = fetch_data()
    write_output(data)
    log.info("Finished")


if __name__ == "__main__":
    scrape()
