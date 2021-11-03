# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html
import json
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper


website = "papersource.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "authority": "www.papersource.com",
    "sec-ch-ua": '"Chromium";v="92", " Not A;Brand";v="99", "Google Chrome";v="92"',
    "sec-ch-ua-mobile": "?0",
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "sec-fetch-site": "none",
    "sec-fetch-mode": "navigate",
    "sec-fetch-user": "?1",
    "sec-fetch-dest": "document",
    "accept-language": "en-US,en;q=0.9,ar;q=0.8",
}


def fetch_data():
    # Your scraper here
    search_url = "https://www.papersource.com/locator"
    search_res = session.get(search_url, headers=headers)

    search_sel = lxml.html.fromstring(search_res.text)

    store_list = search_sel.xpath('//div[contains(@class,"storelist")]//div[@name]')

    all_loc_map_info = (
        search_res.text.split('"items":')[1].split(',"totalRecords":')[0].strip()
    )
    map_list = json.loads(all_loc_map_info)

    for no, store in enumerate(store_list, 0):

        page_url = "".join(store.xpath(".//a/@href")).strip()

        locator_domain = website

        log.info(page_url)
        store_res = session.get(page_url, headers=headers)
        store_sel = lxml.html.fromstring(store_res.text)

        store_info = list(
            filter(
                str,
                [
                    x.strip()
                    for x in store.xpath(
                        './/div[contains(@class,"store-information")]//text()'
                    )
                ],
            )
        )

        full_address = store_info[1:-1]
        street_address = full_address[1].split(":")[-1].strip()
        city = full_address[2].split(":")[-1].strip()
        state = full_address[3].split(":")[-1].strip()
        zip = full_address[4].split(":")[-1].strip()
        country_code = "US"

        location_name = store_info[0].strip()

        phone = list(
            filter(
                str,
                [
                    x.strip()
                    for x in store_sel.xpath('.//a[contains(@href,"tel:")]/text()')
                ],
            )
        )
        if len(phone) > 0:
            phone = phone[0].strip()
        else:
            phone = "<MISSING>"

        store_number = "".join(store.xpath("./@data-amid"))

        location_type = "<MISSING>"
        hours = list(
            filter(
                str,
                [
                    x.strip()
                    for x in store.xpath(
                        './/div[contains(@class,"schedule-table")]//text()'
                    )
                ],
            )
        )
        hours_of_operation = "; ".join(hours).replace("day;", "day:").strip()

        latitude, longitude = map_list[no]["lat"], map_list[no]["lng"]

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
