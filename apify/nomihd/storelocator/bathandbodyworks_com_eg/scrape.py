# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "bathandbodyworks.com.eg"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36",
}


def fetch_data():
    # Your scraper here

    search_urls = [
        "https://www.bathandbodyworks.com/middle-east-and-africa/global-locations-saudiarabia.html",
        "https://www.bathandbodyworks.com/middle-east-and-africa/global-locations-egypt.html",
    ]

    with SgRequests() as session:

        for search_url in search_urls:

            search_res = session.get(search_url, headers=headers)

            search_sel = lxml.html.fromstring(search_res.text)
            stores = search_sel.xpath(
                '//div[contains(@class,"store-location-container")]/div'
            )

            for no, store in enumerate(stores, 1):

                locator_domain = website

                location_type = "<MISSING>"

                page_url = search_url

                location_name = "".join(
                    store.xpath('.//p[@class="store-name"]//text()')
                ).strip()

                store_info = list(
                    filter(
                        str,
                        [x.strip() for x in store.xpath("./p//text()")],
                    )
                )

                street_address = "<MISSING>"

                city = store_info[3]

                state = "<MISSING>"
                zip = "<MISSING>"

                country_code = "".join(
                    store.xpath('.//p[@class="location"]//text()')
                ).strip()

                phone = store_info[-1]

                hours_of_operation = "<MISSING>"

                store_number = "<MISSING>"

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
        deduper=SgRecordDeduper(
            SgRecordID(
                {
                    SgRecord.Headers.LOCATION_NAME,
                    SgRecord.Headers.CITY,
                    SgRecord.Headers.PHONE,
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
