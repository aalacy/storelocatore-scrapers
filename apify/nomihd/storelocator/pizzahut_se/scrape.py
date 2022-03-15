# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper


website = "pizzahut.se"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "Connection": "keep-alive",
    "Cache-Control": "max-age=0",
    "sec-ch-ua": '"Chromium";v="92", " Not A;Brand";v="99", "Google Chrome";v="92"',
    "sec-ch-ua-mobile": "?0",
    "Upgrade-Insecure-Requests": "1",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "Sec-Fetch-Site": "cross-site",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-User": "?1",
    "Sec-Fetch-Dest": "document",
    "Accept-Language": "en-US,en-GB;q=0.9,en;q=0.8",
}


def fetch_data():
    # Your scraper here
    search_url = "https://www.pizzahut.se/restauranger"
    search_res = session.get(search_url, headers=headers)
    search_sel = lxml.html.fromstring(search_res.text)
    stores = search_sel.xpath('//li[@class="restaurants--list_item"]')
    for store in stores:
        page_url = (
            "https://www.pizzahut.se"
            + "".join(store.xpath('.//div[@class="text-left"]/h3/a/@href')).strip()
        )
        locator_domain = website

        location_name = "".join(
            store.xpath('.//div[@class="text-left"]/h3/a/text()')
        ).strip()

        store_info = list(
            filter(
                str,
                [x.strip() for x in store.xpath('.//div[@class="text-left"]/text()')],
            )
        )
        street_address = store_info[0]
        city = ""
        if "," in location_name:
            city = location_name.split(",")[-1].strip()

        state = "<MISSING>"
        zip = "<MISSING>"

        country_code = "SE"

        phone = "".join(
            store.xpath('.//div[@class="text-left"]/a[contains(@href,"tel:")]/text()')
        ).strip()

        store_number = "<MISSING>"

        location_type = "<MISSING>"

        hours_of_operation = ""
        try:
            hours_of_operation = "; ".join(store_info[2:]).strip()
        except:
            pass

        latitude, longitude = "<MISSING>", "<MISSING>"

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
