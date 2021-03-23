# -*- coding: utf-8 -*-
import csv
from sgrequests import SgRequests
from sglogging import sglog
import lxml.html

website = "bootshearingcare.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
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


def get_selector(url):

    response = session.get(url, headers=headers)
    return lxml.html.fromstring(response.text)


def get_store_data(store_sel, page_url):

    log.info(page_url)
    locator_domain = website
    location_name = " ".join(
        store_sel.xpath('//h1[@class="c-location-title"]//span/text()')
    ).strip()
    street_address = "".join(
        store_sel.xpath(
            '//section[@class="nap-unit-inner"]//address[@itemprop="address"]//span[@class="c-address-street-1"]/text()'
        )
    ).strip()

    address_2 = "".join(
        store_sel.xpath(
            '//section[@class="nap-unit-inner"]//address[@itemprop="address"]//span[@class="c-address-street-2"]/text()'
        )
    ).strip()

    if len(address_2) > 0:
        street_address = street_address + ", " + address_2

    city = "".join(
        store_sel.xpath(
            '//section[@class="nap-unit-inner"]//address[@itemprop="address"]//span[@class="c-address-city"]/text()'
        )
    ).strip()

    state = "".join(
        store_sel.xpath(
            '//section[@class="nap-unit-inner"]//address[@itemprop="address"]//span[@class="c-address-state"]/text()'
        )
    ).strip()

    zip = "".join(
        store_sel.xpath(
            '//section[@class="nap-unit-inner"]//address[@itemprop="address"]//span[@class="c-address-postal-code"]/text()'
        )
    ).strip()

    country_code = "".join(
        store_sel.xpath(
            '//section[@class="nap-unit-inner"]//address[@itemprop="address"]/@data-country'
        )
    ).strip()
    store_number = "<MISSING>"
    phone = "".join(
        store_sel.xpath(
            '//div[@class="phones-list"]' '//span[@itemprop="telephone"]/text()'
        )
    ).strip()
    location_type = "<MISSING>"
    latitude = "".join(
        store_sel.xpath(
            '//div[@class="map-wrapper"]' '//meta[@itemprop="latitude"]/@content'
        )
    ).strip()
    longitude = "".join(
        store_sel.xpath(
            '//div[@class="map-wrapper"]' '//meta[@itemprop="longitude"]/@content'
        )
    ).strip()
    hours = store_sel.xpath(
        '//div[@class="c-location-hours"]//table[@class="c-location-hours-details"]'
        "/tbody/tr"
    )

    hours_list = []
    for hour in hours:
        day = "".join(
            hour.xpath('td[@class="c-location-hours-details-row-day"]/text()')
        ).strip()
        time = "".join(
            hour.xpath('td[@class="c-location-hours-details-row-intervals"]//text()')
        ).strip()
        hours_list.append(day + ":" + time)

    hours_of_operation = "; ".join(hours_list).strip()
    if hours_of_operation == "":
        hours_of_operation = "<MISSING>"

    if street_address == "":
        street_address = "<MISSING>"

    if city == "":
        city = "<MISSING>"

    if state == "":
        state = "<MISSING>"

    if phone == "":
        phone = "<MISSING>"

    if latitude == "":
        latitude = "<MISSING>"

    if longitude == "":
        longitude = "<MISSING>"

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

    return curr_list


def fetch_data():
    # Your scraper here
    loc_list = []
    stores_sel = get_selector("https://stores.bootshearingcare.com/index.html")
    stores = stores_sel.xpath('//a[@class="Teaser-titleLink"]/@href')
    for store_url in stores:
        page_url = "https://stores.bootshearingcare.com/" + store_url
        store_sel = get_selector(page_url)
        curr_list = get_store_data(store_sel, page_url)
        loc_list.append(curr_list)

    return loc_list


def scrape():
    log.info("Started")
    data = fetch_data()
    write_output(data)
    log.info("Finished")


if __name__ == "__main__":
    scrape()
