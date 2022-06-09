# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgpostal import sgpostal as parser
import lxml.html
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "timhortons.ph"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.114 Safari/537.36",
}


def fetch_data():
    # Your scraper here

    search_url = "https://www.timhortons.ph/locations"

    with SgRequests() as session:
        search_res = session.get(search_url, headers=headers)
        search_sel = lxml.html.fromstring(search_res.text)

        stores = search_sel.xpath('//div[@class="search-result"]')

        for _, store in enumerate(stores, 1):

            page_url = search_url

            locator_domain = website

            location_name = "".join(
                store.xpath('./div[contains(@class,"search-title")]//text()')
            ).strip()
            if "TEMPORARILY CLOSED" in location_name:
                location_type = "TEMPORARILY CLOSED"
                location_name = location_name.replace("TEMPORARILY CLOSED", "").strip()
            else:
                location_type = "<MISSING>"
            full_address = list(
                filter(
                    str,
                    [
                        x.strip()
                        for x in store.xpath(
                            './/div[contains(@class,"search-address")]//text()'
                        )
                    ],
                )
            )[0].strip()
            raw_address = full_address.strip()
            formatted_addr = parser.parse_address_intl(raw_address)
            street_address = formatted_addr.street_address_1
            if formatted_addr.street_address_2:
                street_address = street_address + ", " + formatted_addr.street_address_2

            if street_address is not None:
                street_address = street_address.replace("Ste", "Suite")
            city = formatted_addr.city
            state = formatted_addr.state
            zip = formatted_addr.postcode

            country_code = "PH"

            store_number = "".join(store.xpath("./@id"))

            phone = (
                list(
                    filter(
                        str,
                        [
                            x.strip()
                            for x in store.xpath(
                                './/div[contains(@class,"search-contact-number")]//text()'
                            )
                        ],
                    )
                )[0]
                .strip()
                .replace("Contact Number:", "")
                .strip()
                .replace("Alfresco dining available", "")
                .strip()
                .split("Delivery")[0]
                .strip()
            )

            hours = list(
                filter(
                    str,
                    [
                        x.strip()
                        for x in store.xpath(
                            './/div[contains(@class,"search-store-hours")]//text()'
                        )
                    ],
                )
            )
            hours_of_operation = "; ".join(hours).replace("Store Hours:", "").strip()
            latitude, longitude = "".join(store.xpath("./@data-lat")), "".join(
                store.xpath("./@data-lng")
            )
            if latitude == "0":
                latitude = "<MISSING>"
            if longitude == "0":
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
                raw_address=raw_address,
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
