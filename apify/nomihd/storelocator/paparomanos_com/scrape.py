# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html
from sgscrape import sgpostal as parser


website = "paparomanos.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.114 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "Accept-Language": "en-US,en;q=0.9,ar;q=0.8",
    "Host": "paparomanos.snappyeats.com",
}


def fetch_data():
    # Your scraper here
    search_url = "http://paparomanos.snappyeats.com/LocationSearch.aspx?Display=all"
    search_res = session.get(search_url, headers=headers, verify="False")
    search_sel = lxml.html.fromstring(search_res.text)

    restaurant_list = search_sel.xpath('//div[@role="main"]//tr[not( ./td/@colspan)]')[
        1:
    ]

    for restaurant in restaurant_list:

        page_url = search_url
        locator_domain = website

        location_name = " ".join(
            restaurant.xpath(
                './/span[contains(@class,"restaurantID")]/following-sibling::span/text()'
            )
        ).strip()

        raw_address = " ".join(
            restaurant.xpath('.//a[contains(@href,"//maps.google")]/parent::td/text()')
        ).strip()

        formatted_addr = parser.parse_address_usa(raw_address)
        street_address = formatted_addr.street_address_1
        if formatted_addr.street_address_2:
            street_address = street_address + ", " + formatted_addr.street_address_2

        city = formatted_addr.city
        state = formatted_addr.state
        zip = formatted_addr.postcode

        country = "US"
        country_code = country

        store_number = "".join(
            restaurant.xpath('.//span[contains(@class,"restaurantID")]/text()')
        ).strip()

        phone = "".join(
            restaurant.xpath(
                './/td[@class="hidden-phone"]/a[contains(@href,"tel")]/text()'
            )
        ).strip()

        location_type = "<MISSING>"

        hours_of_operation = "<MISSING>"

        latitude = "<MISSING>"
        longitude = "<MISSING>"

        yield SgRecord(
            locator_domain=locator_domain,
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=zip,
            country_code=country_code,
            store_number=store_number,
            phone=phone,
            location_type=location_type,
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=hours_of_operation,
            raw_address=raw_address,
        )


def scrape():
    log.info("Started")
    count = 0
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()
