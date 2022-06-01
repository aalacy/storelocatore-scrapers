# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html
from sgpostal import sgpostal as parser
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "pizzaexpressalcaidesa.es"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "Accept-Language": "en-US,en;q=0.9,ar;q=0.8",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.75 Safari/537.36",
}


def fetch_data():
    # Your scraper here

    search_url = "https://pizzaexpressalcaidesa.es"

    with SgRequests() as session:
        search_res = session.get(search_url, headers=headers)

        search_sel = lxml.html.fromstring(search_res.text)

        stores = search_sel.xpath('//*[@class="our-pizzerias"]//div[a]')

        for store in stores:

            locator_domain = website

            page_url = store.xpath("./a/@href")[0]
            if "http" not in page_url:
                page_url = "https://pizzaexpressalcaidesa.es" + page_url

            location_name = "".join(store.xpath("./a//text()")).strip()

            store_info = list(
                filter(
                    str,
                    [x.strip() for x in store.xpath(".//p//text()")],
                )
            )
            location_type = "<MISSING>"
            if "\r\n" in store_info[0]:
                raw_address = store_info[0].split("\r\n")[0].strip()
                phone = store_info[0].split("\r\n")[1].strip()
                hours_of_operation = store_info[0].split("\r\n")[-1]
            else:
                raw_address = store_info[0].strip()
                phone = store_info[1].strip()
                hours_of_operation = store_info[-1].strip()
            formatted_addr = parser.parse_address_intl(raw_address)
            street_address = formatted_addr.street_address_1
            if formatted_addr.street_address_2:
                street_address = street_address + ", " + formatted_addr.street_address_2

            if street_address is not None:
                street_address = street_address.replace("Ste", "Suite")

            city = formatted_addr.city

            state = formatted_addr.state
            zip = formatted_addr.postcode

            country_code = "ES"

            store_number = "<MISSING>"
            latitude = longitude = "<MISSING>"

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
