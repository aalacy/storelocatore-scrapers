# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html
from sgpostal import sgpostal as parser
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "bathandbodyworks.in"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "Accept-Language": "en-US,en;q=0.9,ar;q=0.8",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.75 Safari/537.36",
}


def fetch_data():
    # Your scraper here
    search_url = "https://www.bathandbodyworks.in/bbw-store-locator.html"

    with SgRequests() as session:
        search_res = session.get(search_url, headers=headers)

        search_sel = lxml.html.fromstring(search_res.text)

        stores = search_sel.xpath('//div[@class="store_address"]/..')

        for no, store in enumerate(stores, 1):

            locator_domain = website

            page_url = search_url + str(no)

            location_name = "".join(
                store.xpath('.//div[@class="store_title"]/text()')
            ).strip()

            location_type = "<MISSING>"

            store_info = list(
                filter(
                    str,
                    [
                        x.strip()
                        for x in store.xpath('.//p[@class="store_addressline"]//text()')
                    ],
                )
            )

            raw_address = (
                " ".join(store_info)
                .strip('" ')
                .replace("MAJOR BRANDS INDIA PVT LTD, BATH & BODY WORKS,", "")
                .strip()
            )

            formatted_addr = parser.parse_address_intl(raw_address)
            street_address = formatted_addr.street_address_1
            if formatted_addr.street_address_2:
                street_address = street_address + ", " + formatted_addr.street_address_2

            if street_address is not None:
                street_address = street_address.replace("Ste", "Suite")

            city = formatted_addr.city

            state = formatted_addr.state
            zip = formatted_addr.postcode

            if not state:
                if zip and "-" in zip:
                    state = zip.split("-")[0].strip()
                    zip = zip.split("-")[1].strip()

            if not zip:
                if city and "-" in city:
                    zip = city.split("-")[1].strip()
                    city = city.split("-")[0].strip()

            country_code = formatted_addr.country

            store_number = "".join(
                store.xpath('.//span[@class="store-number"]/text()')
            ).strip(" .")
            phone = "<MISSING>"

            hours_of_operation = "<MISSING>"
            map_info = "".join(store.xpath("./@str_lati/@value"))

            latitude, longitude = (
                "".join(store.xpath("./@str_lati/@value")).strip(),
                "".join(store.xpath("./@str_longi/@value")).strip(),
            )

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
