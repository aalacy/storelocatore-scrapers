# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "kellysroastbeef.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()

headers = {
    "authority": "kellysroastbeef.com",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "accept-language": "en-US,en-GB;q=0.9,en;q=0.8",
    "referer": "https://kellysroastbeef.com/",
    "sec-ch-ua": '" Not A;Brand";v="99", "Chromium";v="102", "Google Chrome";v="102"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "sec-fetch-dest": "document",
    "sec-fetch-mode": "navigate",
    "sec-fetch-site": "same-origin",
    "sec-fetch-user": "?1",
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36",
}


def fetch_data():
    # Your scraper here
    search_url = "https://kellysroastbeef.com/locations/"
    search_req = session.post(search_url, headers=headers)
    search_sel = lxml.html.fromstring(search_req.text)
    stores = search_sel.xpath(
        '//div[contains(@class,"et_pb_row_inner et_pb_row_inner_")]'
    )
    for store in stores:
        page_url = search_url
        store_number = "<MISSING>"
        locator_domain = website

        location_name = "".join(store.xpath("div[1]/div[1]//h2/text()")).strip()

        raw_address = store.xpath("div[1]/div[3]//p[1]/text()")
        street_address = raw_address[0]
        city = raw_address[-1].strip().split(",")[0].strip()
        state = raw_address[-1].strip().split(",")[-1].strip().split(" ")[0].strip()
        zip = raw_address[-1].strip().split(",")[-1].strip().split(" ")[-1].strip()

        country_code = "US"
        phone = "".join(store.xpath("div[1]/div[3]//p[2]//text()")).strip()
        location_type = "<MISSING>"

        hours_of_operation = "".join(store.xpath("div[1]/div[3]//p[3]//text()")).strip()

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
        )


def scrape():
    log.info("Started")
    count = 0
    with SgWriter(
        deduper=SgRecordDeduper(
            SgRecordID(
                {
                    SgRecord.Headers.STREET_ADDRESS,
                    SgRecord.Headers.CITY,
                    SgRecord.Headers.ZIP,
                }
            )
        )
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()
