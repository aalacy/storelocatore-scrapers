# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
import lxml.html

website = "pizzahut.sk"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "authority": "www.pizzahut.sk",
    "cache-control": "max-age=0",
    "sec-ch-ua": '"Chromium";v="92", " Not A;Brand";v="99", "Google Chrome";v="92"',
    "sec-ch-ua-mobile": "?0",
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "sec-fetch-site": "same-origin",
    "sec-fetch-mode": "navigate",
    "sec-fetch-user": "?1",
    "sec-fetch-dest": "document",
    "accept-language": "en-US,en-GB;q=0.9,en;q=0.8",
}


def fetch_data():
    # Your scraper here
    search_url = "https://www.pizzahut.sk/en"
    search_res = session.get(search_url, headers=headers)
    search_sel = lxml.html.fromstring(search_res.text)
    stores = search_sel.xpath(
        '//div[@class="_1Q9if"][./p[@class="font_7"] and count(p)=3]'
    )

    for store in stores:

        page_url = search_url
        locator_domain = website
        raw_info = store.xpath("p")
        raw_list = []
        for raw in raw_info:
            raw_list.append("".join(raw.xpath(".//text()")).strip())

        location_name = "".join(raw_list[0]).strip()
        street_address = "".join(raw_list[1]).strip()
        city_zip = "".join(raw_list[-1]).strip()
        city = city_zip.rsplit(" ", 1)[-1].strip()
        state = "<MISSING>"
        zip = city_zip.rsplit(" ", 1)[0].strip()
        country_code = "SK"

        phone = "<MISSING>"
        store_number = "<MISSING>"
        location_type = "<MISSING>"
        hours_of_operation = "<MISSING>"
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
        deduper=SgRecordDeduper(SgRecordID({SgRecord.Headers.LOCATION_NAME}))
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()
