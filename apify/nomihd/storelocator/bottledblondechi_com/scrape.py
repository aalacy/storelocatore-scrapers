# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "bottledblondechi.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "Connection": "keep-alive",
    "sec-ch-ua": '" Not;A Brand";v="99", "Google Chrome";v="91", "Chromium";v="91"',
    "sec-ch-ua-mobile": "?0",
    "Upgrade-Insecure-Requests": "1",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "Sec-Fetch-Site": "same-origin",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-User": "?1",
    "Sec-Fetch-Dest": "document",
    "Accept-Language": "en-US,en-GB;q=0.9,en;q=0.8",
}


def fetch_data():
    # Your scraper here
    search_url = "https://bottledblondepizzeria.com/"
    stores_req = session.get(search_url, headers=headers)
    stores_sel = lxml.html.fromstring(stores_req.text)
    stores = stores_sel.xpath('//a[@class="column-link"]/@href')
    for store_url in stores:
        page_url = "https://bottledblondepizzeria.com" + store_url + "-contact/"
        log.info(page_url)
        store_req = session.get(page_url, headers=headers)
        if store_req.ok:
            if "OPENING" in store_req.text:
                continue
            store_sel = lxml.html.fromstring(store_req.text)

            locator_domain = website

            location_name = "".join(
                store_sel.xpath("//div[@class='contact-lc-title']/text()")
            ).strip()

            raw_list = (
                "".join(
                    store_sel.xpath("//p[./i[@class='fa fa-map-marker']]/span/text()")
                )
                .strip()
                .split(",")
            )
            street_address = raw_list[0].strip().split("(")[0].strip()
            city = raw_list[1].strip()
            state_zip = raw_list[-1].strip()
            state = state_zip.split(" ")[0].strip()
            zip = state_zip.split(" ")[-1].strip()

            country_code = "US"

            store_number = "<MISSING>"

            phone = store_sel.xpath(
                '//p[contains(text(),"Dinner Reservations")]/a/text()'
            )
            if len(phone) > 0:
                phone = phone[0]

            location_type = "<MISSING>"
            hours_of_operation = (
                "; ".join(
                    store_sel.xpath("//p[./span/b[contains(text(),'HOURS')]]//text()")
                )
                .strip()
                .replace("\n", "")
                .replace("*Food served until closing", "")
                .strip()
                .replace("HOURS; ;", "")
                .strip()
                .replace(":;", ":")
                .replace(": ;", ":")
                .replace("; ;", ";")
                .replace("day :", "day:")
                .strip()
            )

            latitude = "".join(
                store_sel.xpath('//div[@class="map-marker"]/@data-lat')
            ).strip()
            longitude = "".join(
                store_sel.xpath('//div[@class="map-marker"]/@data-lng')
            ).strip()

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
