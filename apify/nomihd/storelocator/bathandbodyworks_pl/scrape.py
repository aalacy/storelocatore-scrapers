# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html
from sgpostal import sgpostal as parser
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "www.bathandbodyworks.pl"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.114 Safari/537.36",
}


def fetch_data():
    # Your scraper here

    search_url = "https://www.bathandbodyworks.com/europe/global-locations-poland.html"

    with SgRequests() as session:
        search_res = session.get(search_url, headers=headers)
        search_sel = lxml.html.fromstring(search_res.text)

        stores = search_sel.xpath('//div[@class="store-location"]')

        for _, store in enumerate(stores, 1):

            page_url = search_url

            locator_domain = website

            location_name = "".join(
                store.xpath('./p[@class="store-name"]/text()')
            ).strip()
            store_info = list(
                filter(
                    str,
                    [
                        x.strip()
                        for x in store.xpath(
                            './p[text()="Location"]/following-sibling::p[1]//text()'
                        )
                    ],
                )
            )

            raw_address = "<MISSING>"
            street_address = store_info[0].strip(", ").strip()
            city = store_info[-1].strip()
            state = "<MISSING>"

            zip = "<MISSING>"
            country_code = "".join(store.xpath('./p[@class="location"]/text()')).strip()

            store_number = "<MISSING>"
            phone = "".join(
                store.xpath(
                    './p[text()="Phone Number"]/following-sibling::p[1]//text()'
                )
            ).strip()
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
                raw_address=raw_address,
            )


def scrape():
    log.info("Started")
    count = 0
    with SgWriter(
        deduper=SgRecordDeduper(record_id=RecommendedRecordIds.PhoneNumberId)
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()
