# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html
from sgscrape import sgpostal as parser

website = "arabianoud-usa.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "Connection": "keep-alive",
    "Cache-Control": "max-age=0",
    "sec-ch-ua": '" Not;A Brand";v="99", "Google Chrome";v="91", "Chromium";v="91"',
    "sec-ch-ua-mobile": "?0",
    "Upgrade-Insecure-Requests": "1",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "Sec-Fetch-Site": "cross-site",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-User": "?1",
    "Sec-Fetch-Dest": "document",
    "Accept-Language": "en-US,en-GB;q=0.9,en;q=0.8",
}


def fetch_data():
    # Your scraper here
    search_url = "https://www.arabianoud-usa.com/our-store"
    stores_req = session.get(search_url, headers=headers)
    stores_sel = lxml.html.fromstring(stores_req.text)
    names = stores_sel.xpath(
        '//ul[@class="store-address"]/li[contains(text(),"Arabian Oud")]/text()'
    )
    addresses = stores_sel.xpath(
        '//ul[@class="store-address"]/li[.//a[contains(text(),"Get direction")]]/text()'
    )
    coordinates = stores_sel.xpath(
        '//ul[@class="store-address"]/li[.//a[contains(text(),"Get direction")]]/a/@href'
    )
    phones = stores_sel.xpath(
        '//ul[@class="store-address"]/li[.//i[contains(@class,"fa fa-phone")]]/text()'
    )

    hours = stores_sel.xpath(
        '//ul[@class="store-address"]/li[.//i[contains(@class,"far fa-clock")]]/text()'
    )
    hours = [x.strip() for x in hours]
    for index in range(0, len(names)):
        page_url = search_url
        locator_domain = website

        location_name = "".join(names[index]).strip()

        raw_address = "".join(addresses[index]).strip()
        formatted_addr = parser.parse_address_usa(raw_address)
        street_address = formatted_addr.street_address_1
        if formatted_addr.street_address_2:
            street_address = street_address + ", " + formatted_addr.street_address_2

        city = formatted_addr.city
        state = formatted_addr.state
        zip = formatted_addr.postcode

        country_code = "US"

        store_number = "<MISSING>"

        phone = "".join(phones[index]).strip().split(",")[0].strip()
        location_type = "<MISSING>"
        hours_of_operation = "; ".join(hours).strip()
        map_link = coordinates[index]
        latitude = "<MISSING>"
        longitude = "<MISSING>"

        if "/@" in map_link:
            latitude = map_link.split("/@")[1].strip().split(",")[0].strip()
            longitude = map_link.split("/@")[1].strip().split(",")[1]

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
