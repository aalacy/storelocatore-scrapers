# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import json
import lxml.html
from sgpostal import sgpostal as parser
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "assistinghands.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.114 Safari/537.36",
}


def fetch_data():
    # Your scraper here

    search_url = "https://assistinghands.com/wp-json/wpgmza/v1/features/?filter=%7B%22map_id%22%3A%222%22%2C%22mashupIDs%22%3A%5B%5D%2C%22customFields%22%3A%5B%5D%7D"
    with SgRequests() as session:
        search_res = session.get(search_url, headers=headers)

        stores = json.loads(search_res.text)["markers"]

        for store in stores:
            page_url = "<MISSING>"
            phone = "<MISSING>"

            if len(store["description"]) > 0:
                store_sel = lxml.html.fromstring(store["description"])

                page_url = "".join(
                    store_sel.xpath('//a[contains(text(),"Visit Website")]/@href')
                ).strip()
                phone = "".join(
                    store_sel.xpath('//p/a[contains(@href,"tel:")]//text()')
                ).strip()
                if len(phone) <= 0:
                    phone = store_sel.xpath("//p//text()")
                    if len(phone) > 0:
                        phone = phone[0].strip()

            locator_domain = website

            location_name = store["title"]

            raw_address = store["address"]

            formatted_addr = parser.parse_address_usa(raw_address)
            street_address = formatted_addr.street_address_1
            if formatted_addr.street_address_2:
                street_address = street_address + ", " + formatted_addr.street_address_2

            if street_address is not None:
                street_address = street_address.replace("Ste", "Suite")
            city = formatted_addr.city

            if formatted_addr.state is not None:
                state = formatted_addr.state.replace(", Usa", "").strip()

            zip = formatted_addr.postcode

            country_code = "US"
            if zip and " " in zip:
                country_code = "CA"

            if not zip:
                zip = "32819"

            store_number = store["id"]

            location_type = "<MISSING>"

            hours_of_operation = "<MISSING>"

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
