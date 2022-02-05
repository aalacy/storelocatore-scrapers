# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper


website = "securitypublicstorage.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "Connection": "keep-alive",
    "Cache-Control": "max-age=0",
    "sec-ch-ua": '"Google Chrome";v="93", " Not;A Brand";v="99", "Chromium";v="93"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "Upgrade-Insecure-Requests": "1",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.63 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "Sec-Fetch-Site": "cross-site",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-User": "?1",
    "Sec-Fetch-Dest": "document",
    "Accept-Language": "en-US,en-GB;q=0.9,en;q=0.8",
}


def fetch_data():
    # Your scraper here
    search_url = "https://www.securitypublicstorage.com/locations"
    search_res = session.get(search_url, headers=headers)

    search_sel = lxml.html.fromstring(search_res.text)

    store_list = search_sel.xpath('//div[@class="dp-dfg-items"]/article')

    for store in store_list:

        page_url = "".join(store.xpath('.//h2[@class="entry-title"]/a/@href')).strip()
        log.info(page_url)
        store_req = session.get(page_url, headers=headers)
        store_sel = lxml.html.fromstring(store_req.text)

        locator_domain = website
        location_name = "".join(
            store.xpath('.//h2[@class="entry-title"]//text()')
        ).strip()

        street_address = "".join(
            store.xpath(
                './/p[@class="dp-dfg-custom-field dp-dfg-cf-street_address"]/span/text()'
            )
        ).strip()

        city = "".join(
            store.xpath('.//p[@class="dp-dfg-custom-field dp-dfg-cf-city"]/span/text()')
        ).strip()
        state = "".join(
            store.xpath(
                './/p[@class="dp-dfg-custom-field dp-dfg-cf-state"]/span/text()'
            )
        ).strip()
        zip = "".join(
            store.xpath('.//p[@class="dp-dfg-custom-field dp-dfg-cf-zip"]/span/text()')
        ).strip()
        country_code = "US"

        store_number = "<MISSING>"

        location_type = "<MISSING>"
        phone = "".join(store_sel.xpath('//div[@class="phonebutton"]//text()')).strip()
        hours_of_operation = "".join(
            store_sel.xpath('//div[./strong[text()="Office Hours:"]]/text()')
        ).strip()
        if len(hours_of_operation) <= 0:
            hours_of_operation = "".join(
                store_sel.xpath('//div[@class="office-hours"]/text()')
            ).strip()
        latitude, longitude = "<MISSING>", "<MISSING>"

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
