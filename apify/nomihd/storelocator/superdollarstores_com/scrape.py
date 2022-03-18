# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "superdollarstores.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)

session = SgRequests()
headers = {
    "Proxy-Connection": "keep-alive",
    "Cache-Control": "max-age=0",
    "Upgrade-Insecure-Requests": "1",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.72 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "Accept-Language": "en-US,en;q=0.9,ar;q=0.8",
}


def fetch_data():
    # Your scraper here

    search_url = "http://superdollarstores.com/locations"

    search_res = session.get(search_url, headers=headers)
    search_sel = lxml.html.fromstring(search_res.text)
    stores_list = search_sel.xpath(
        '//div[@id="listings"]//div[contains(@class,"lsrow")]'
    )

    for store in stores_list:

        page_url = search_url
        locator_domain = website

        location_name = "".join(store.xpath(".//h3/span/text()")).strip()

        address_info = list(
            filter(
                str,
                store.xpath('.//p[@class="address"]//text()'),
            )
        )

        street_address = " ".join(address_info[:-4]).strip(" ,")

        city = address_info[-4].strip(" ,")

        state = address_info[-2].strip(" ,")
        zip = address_info[-1].strip(" ,")

        country_code = "US"

        store_number = "<MISSING>"
        try:
            store_number = location_name.rsplit(" ", 1)[-1].strip()
        except:
            pass
        phone = "".join(
            store.xpath(
                './/div[contains(@class,"telephone")]/span[@class="output"]/text()'
            )
        ).strip()

        location_type = "<MISSING>"

        hours_of_operation = "".join(
            store.xpath(
                './/span[contains(text(),"Hours of Operation")]/following-sibling::span/text()'
            )
        ).strip()

        latitude = "<MISSING>"
        longitude = "<MISSING>"

        raw_address = "<MISSING>"
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
        deduper=SgRecordDeduper(record_id=RecommendedRecordIds.StoreNumberId)
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()
