# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "dabella.us"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "authority": "dabella.us",
    "sec-ch-ua": '" Not A;Brand";v="99", "Chromium";v="90", "Google Chrome";v="90"',
    "sec-ch-ua-mobile": "?0",
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "sec-fetch-site": "none",
    "sec-fetch-mode": "navigate",
    "sec-fetch-user": "?1",
    "sec-fetch-dest": "document",
    "accept-language": "en-US,en;q=0.9,ar;q=0.8",
}


def fetch_data():
    # Your scraper here
    search_url = "https://dabella.us/contact/#locations"
    search_res = session.get(search_url, headers=headers)

    search_sel = lxml.html.fromstring(search_res.text)
    store_list = search_sel.xpath('//div[contains(@class,"location-card ")]')

    for store in store_list:
        page_url = store.xpath("./div/a/@href")[0].strip()

        locator_domain = website

        log.info(page_url)
        store_res = session.get(page_url, headers=headers)
        store_sel = lxml.html.fromstring(store_res.text)

        raw_address = "<MISSING>"

        street_address = " ".join(
            store.xpath('.//span[@itemprop="streetAddress"]//text()')
        ).strip()
        city = " ".join(
            store.xpath('.//span[@itemprop="addressLocality"]//text()')
        ).strip()
        state = " ".join(
            store.xpath('.//span[@itemprop="addressRegion"]//text()')
        ).strip()
        zip = " ".join(store.xpath('.//span[@itemprop="postalCode"]//text()')).strip()
        country_code = "US"

        location_name = " ".join(store.xpath('.//*[@itemprop="name"]//text()')).strip()

        raw_phone = list(
            filter(
                str,
                [
                    x.strip()
                    for x in store_sel.xpath(
                        '//a[contains(@href,"tel:")]//text() | //tr[td="Phone"]/td[2]/text()'
                    )
                ],
            )
        )
        phone = " ".join(raw_phone[:1]).strip()
        store_number = (
            store_res.text.split('"id":')[1].split(",")[0].strip('" ').strip()
        )
        location_type = "<MISSING>"

        hours_of_operation = raw_phone[-1].strip()
        latitude, longitude = (
            store_res.text.split('"map_start_lat":"')[1]
            .split(",")[0]
            .replace('"', "")
            .strip(),
            store_res.text.split('"map_start_lng":"')[1]
            .split(",")[0]
            .replace('"', "")
            .strip(),
        )
        if latitude == "0":
            latitude = "<MISSING>"
        if longitude == "0":
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
