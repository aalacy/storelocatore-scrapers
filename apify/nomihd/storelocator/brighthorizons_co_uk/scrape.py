# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
import lxml.html
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import json
from sgscrape import sgpostal as parser

website = "brighthorizons.co.uk"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36",
    "Accept": "application/json",
}


def fetch_data():
    # Your scraper here

    search_url = (
        "https://www.brighthorizons.co.uk/Nursery-Results?q=E1%206AN&distance=250000"
    )
    stores_req = session.get(search_url, headers=headers)
    stores_sel = lxml.html.fromstring(stores_req.text)

    stores = stores_sel.xpath('//div[@class="search-result__content"]/a/@href')
    for store_url in stores:
        page_url = ""
        if "http" not in store_url:
            page_url = "https://www.brighthorizons.co.uk" + store_url
        else:
            page_url = store_url

        log.info(page_url)
        store_req = session.get(page_url, headers=headers)
        store_sel = lxml.html.fromstring(store_req.text)
        store_json = json.loads(
            "".join(
                store_sel.xpath('//script[@type="application/ld+json"]/text()')
            ).strip(),
            strict=False,
        )

        location_type = "<MISSING>"
        locator_domain = website
        location_name = store_json["name"]

        raw_address = store_json["address"]
        formatted_addr = parser.parse_address_intl(raw_address)
        street_address = formatted_addr.street_address_1
        if formatted_addr.street_address_2:
            street_address = street_address + ", " + formatted_addr.street_address_2

        city = formatted_addr.city
        state = formatted_addr.state
        zip = formatted_addr.postcode
        country_code = "GB"

        temp_phone = store_sel.xpath('//span[contains(@class,"rTapNumber")]/text()')
        phone = ""
        if len(temp_phone) > 0:
            phone = temp_phone[0].strip()

        hours_of_operation = store_json["openingHours"]
        store_number = "<MISSING>"

        latitude = ""
        longitude = ""
        map_link = store_sel.xpath('//iframe[@class="map-card__map"]/@src')
        if len(map_link) > 0:
            map_link = map_link[0]
            latitude = map_link.split("?q=")[1].strip().split(",")[0].strip()
            longitude = (
                map_link.split("?q=")[1]
                .strip()
                .split(",")[1]
                .strip()
                .split("&")[0]
                .strip()
            )

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
