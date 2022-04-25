# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html
from sgpostal import sgpostal as parser
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "suviche.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.114 Safari/537.36",
}


def fetch_data():
    # Your scraper here

    search_url = "https://suviche.com/locations/"

    with SgRequests() as session:
        search_res = session.get(search_url, headers=headers)

        search_sel = lxml.html.fromstring(search_res.text)

        stores = search_sel.xpath(
            '//div[@class="wpb_wrapper"][./div[@class="wpb_text_column wpb_content_element  title-location"]]'
        )

        for store in stores:

            page_url = search_url
            locator_domain = website

            location_name = "".join(
                store.xpath(
                    'div[@class="wpb_text_column wpb_content_element  title-location"]//h2//text()'
                )
            ).strip()
            raw_address = list(
                filter(
                    str,
                    [
                        x.strip()
                        for x in store.xpath(
                            "div[@class='wpb_text_column wpb_content_element '][1]/div/p//text()"
                        )
                    ],
                )
            )

            raw_address = "".join(raw_address).strip()
            formatted_addr = parser.parse_address_usa(raw_address)
            street_address = formatted_addr.street_address_1
            if formatted_addr.street_address_2:
                street_address = street_address + ", " + formatted_addr.street_address_2

            if street_address is not None:
                street_address = street_address.replace("Ste", "Suite")
            city = formatted_addr.city
            state = formatted_addr.state
            zip = formatted_addr.postcode

            country_code = "US"

            store_number = "<MISSING>"

            phone = "".join(store.xpath('.//div[@class="iwithtext"]//text()')).strip()

            location_type = "<MISSING>"

            hours = list(
                filter(
                    str,
                    [
                        x.strip()
                        for x in store.xpath(
                            "div[@class='wpb_text_column wpb_content_element '][2]/div/p/text()"
                        )
                    ],
                )
            )
            hours_of_operation = (
                "; ".join(hours)
                .replace(
                    "Find us on the third base line across from sections 22 & 23.", ""
                )
                .strip()
            )

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
