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
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "Accept-Language": "en-US,en-GB;q=0.9,en;q=0.8",
    "Connection": "keep-alive",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "none",
    "Sec-Fetch-User": "?1",
    "Upgrade-Insecure-Requests": "1",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36",
    "sec-ch-ua": '" Not A;Brand";v="99", "Chromium";v="102", "Google Chrome";v="102"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
}


def fetch_data():
    # Your scraper here

    search_url = "http://superdollarstores.com/locations"

    search_res = session.get(search_url, headers=headers)
    search_sel = lxml.html.fromstring(search_res.text)
    stores_list = search_sel.xpath(
        '//div[@class="elementor-widget-wrap elementor-element-populated"][.//a[contains(text(),"Click to view the ad")]]'
    )

    for store in stores_list:

        page_url = search_url
        locator_domain = website

        location_name = "".join(
            store.xpath(
                ".//h3[@class='elementor-heading-title elementor-size-default']/text()"
            )
        ).strip()

        store_info = list(
            filter(
                str,
                store.xpath(
                    './/div[@class="elementor-widget-container"][./p/a[contains(text(),"Click to view the ad")]]/p/text()'
                ),
            )
        )

        raw_address = store_info[0].split(",")
        street_address = ", ".join(raw_address[:-3]).strip()
        city = raw_address[-3].strip()
        state = raw_address[-2].strip()
        zip = raw_address[-1].strip()

        country_code = "US"

        store_number = "<MISSING>"
        try:
            store_number = location_name.rsplit(" ", 1)[-1].strip()
        except:
            pass
        phone = store_info[1].strip().replace("Telephone:", "").strip()

        location_type = "<MISSING>"

        hours_of_operation = (
            store_info[-1].strip().replace("Hours of Operation:", "").strip()
        )

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
