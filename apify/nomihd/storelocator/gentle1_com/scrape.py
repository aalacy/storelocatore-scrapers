# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
import lxml.html
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
import json

website = "gentle1.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()

headers = {
    "authority": "www.interdent.com",
    "cache-control": "max-age=0",
    "sec-ch-ua": '"Chromium";v="92", " Not A;Brand";v="99", "Google Chrome";v="92"',
    "sec-ch-ua-mobile": "?0",
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "sec-fetch-site": "cross-site",
    "sec-fetch-mode": "navigate",
    "sec-fetch-user": "?1",
    "sec-fetch-dest": "document",
    "accept-language": "en-US,en-GB;q=0.9,en;q=0.8",
}


def fetch_data():
    # Your scraper here

    search_url = "https://www.interdent.com/gentle-dental/locations/"
    stores_req = session.get(search_url, headers=headers)
    stores = json.loads(
        stores_req.text.split("gd_data = ")[1].strip().split("}],")[0].strip() + "}]"
    )

    for store in stores:

        page_url = store["url"]
        log.info(page_url)
        store_req = session.get(page_url, headers=headers)
        store_sel = lxml.html.fromstring(store_req.text)

        location_name = store["title"]
        location_type = "<MISSING>"
        locator_domain = website

        raw_address = store["address"].split("\n")
        street_address = ", ".join(raw_address[:-1]).strip()
        city = raw_address[-1].strip().split(",")[0].strip()
        state_zip = raw_address[-1].strip().split(",")[-1].strip()
        state = state_zip.split(" ")[0].strip()
        zip = state_zip.split(" ")[-1].strip()

        country_code = "US"
        store_number = "<MISSING>"
        phone = store_sel.xpath('//a[@class="x-btn x-btn-global red-btn"]/text()')
        if len(phone) > 0:
            phone = "".join(phone[0]).strip()

        hours = list(filter(str, store_sel.xpath('//span[@class="loc_hours"]//text()')))

        hours_of_operation = (
            "; ".join(hours)
            .strip()
            .replace("\n", "")
            .split("; ; Service representatives standing by")[0]
            .strip()
        )

        latitude = store["lat"]
        longitude = store["lng"]

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
