# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
import lxml.html
from sgpostal import sgpostal as parser

website = "pizzahut.co.il"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "sec-ch-ua": '"Chromium";v="92", " Not A;Brand";v="99", "Google Chrome";v="92"',
    "sec-ch-ua-mobile": "?0",
    "Upgrade-Insecure-Requests": "1",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36",
}


def fetch_data():
    # Your scraper here
    search_url = "https://pizzahut.co.il/branch/"
    search_res = session.get(search_url, headers=headers)
    search_sel = lxml.html.fromstring(search_res.text)
    stores = search_sel.xpath('//li[@class="menu-col"]/ul/li/a/@href')

    for store_url in stores:
        if "/branch/" not in store_url:
            continue
        page_url = store_url
        log.info(page_url)
        store_req = session.get(page_url, headers=headers)
        store_sel = lxml.html.fromstring(store_req.text)

        locator_domain = website
        location_name = "".join(
            store_sel.xpath('//div[@id="branch-info"]/header/h2/text()')
        ).strip()
        raw_address = "".join(
            store_sel.xpath(
                '//div[@id="branch-info"]/div[@id="branch-details"]//div[@class="adress"]/span/text()'
            )
        ).strip()
        formatted_addr = parser.parse_address_intl(raw_address)
        street_address = formatted_addr.street_address_1
        if formatted_addr.street_address_2:
            street_address = street_address + ", " + formatted_addr.street_address_2

        city = formatted_addr.city
        state = formatted_addr.state
        zip = formatted_addr.postcode

        country_code = "IL"

        phone = "".join(
            store_sel.xpath(
                '//div[@id="branch-info"]/div[@id="branch-details"]//div[@class="phone"]//text()'
            )
        ).strip()
        store_number = "<MISSING>"
        location_type = "<MISSING>"
        hours = list(
            filter(
                str, store_sel.xpath('//div[@class="branch_opening_hours"]/p/text()')
            )
        )

        hours_of_operation = "; ".join(hours).strip()
        map_link = "".join(store_sel.xpath('//div[@class="waze-link"]/a/@href')).strip()
        latitude = map_link.split("ll=")[1].strip().split(",")[0].strip()
        longitude = map_link.split("ll=")[1].strip().split(",")[-1].strip()

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
    with SgWriter(
        deduper=SgRecordDeduper(record_id=RecommendedRecordIds.PageUrlId)
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()
