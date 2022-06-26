# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgpostal import sgpostal as parser
import lxml.html
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "oporto.co.nz"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36",
}


def fetch_data():
    # Your scraper here
    search_url = "https://www.oporto.co.nz/locations/"

    with SgRequests() as session:
        search_res = session.get(search_url, headers=headers)

        search_sel = lxml.html.fromstring(search_res.text)
        stores = search_sel.xpath('//div[@class="store-details"]')

        for store in stores:

            locator_domain = website

            location_name = "".join(
                store.xpath('.//p[@class="store-name"]//text()')
            ).strip()

            location_type = "<MISSING>"

            raw_address = "".join(store.xpath('.//p[@class="store-suburb"]//text()'))

            street_address = "".join(
                store.xpath('.//p[@class="store-address"]//text()')
            )

            raw_address = street_address + " " + raw_address
            formatted_addr = parser.parse_address_intl(raw_address)

            city = formatted_addr.city

            state = formatted_addr.state
            zip = formatted_addr.postcode

            country_code = "NZ"

            phone = "".join(store.xpath('.//p[@class="store-number"]//text()'))

            page_url = search_url
            hours = list(
                filter(
                    str,
                    [
                        x.strip()
                        for x in store.xpath('.//p[@class="store-open"]//text()')
                    ],
                )
            )
            hours_of_operation = "; ".join(hours)

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
                raw_address=raw_address,
            )


def scrape():
    log.info("Started")
    count = 0
    with SgWriter(
        deduper=SgRecordDeduper(SgRecordID({SgRecord.Headers.RAW_ADDRESS}))
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()
