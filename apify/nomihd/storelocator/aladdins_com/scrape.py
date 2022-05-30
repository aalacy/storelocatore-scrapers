# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper


website = "aladdins.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "authority": "aladdins.com",
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
    search_url = "https://aladdins.com/locations/"
    search_res = session.get(search_url, headers=headers)

    search_sel = lxml.html.fromstring(search_res.text)

    store_list = search_sel.xpath('//div[@class="locations-item"]')

    for store in store_list:

        page_url = search_url

        locator_domain = website

        store_info = list(
            filter(
                str,
                [
                    x.strip()
                    for x in store.xpath('.//div[@class="location-address"]//text()')
                ],
            )
        )

        street_address = store_info[0].strip()
        city = store_info[-1].split(",")[0].strip()
        state = store_info[-1].split(" ")[-2].strip()
        zip = store_info[-1].split(" ")[-1].strip()
        country_code = "US"

        location_name = "".join(store.xpath(".//h2//text()")).strip()
        if "coming soon" in location_name.lower():
            continue
        phone = list(
            filter(
                str,
                [x.strip() for x in store.xpath('.//a[contains(@href,"tel:")]/text()')],
            )
        )
        if len(phone) > 0:
            phone = phone[0].strip()
        else:
            phone = "<MISSING>"

        store_number = "".join(store.xpath("./@data-id"))

        location_type = "<MISSING>"
        hours = list(
            filter(
                str,
                [
                    x.strip()
                    for x in store.xpath('.//div[@class="location-times"]//text()')
                ],
            )
        )
        hours_of_operation = (
            "; ".join(hours).replace("Now Open!;", "").replace(":;", ":").strip()
        )
        latitude, longitude = "".join(store.xpath("./@data-lat")), "".join(
            store.xpath("./@data-lng")
        )

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
