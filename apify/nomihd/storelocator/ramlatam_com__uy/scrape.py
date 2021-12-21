# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgpostal import sgpostal as parser
import lxml.html
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "ramlatam.com/uy"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36",
}


def fetch_data():
    # Your scraper here
    search_url = "https://www.ramlatam.com/uy/sucursales/"

    with SgRequests() as session:
        search_res = session.get(search_url, headers=headers)

        search_sel = lxml.html.fromstring(search_res.text)
        stores = search_sel.xpath("//h4/following-sibling::p")

        for no, store in enumerate(stores, 1):

            locator_domain = website
            store_info = list(
                filter(
                    str,
                    [x.strip() for x in store.xpath(".//text()")],
                )
            )

            store_info = " ".join(store_info)

            location_name = store.xpath(".//preceding::h3//text()")[-1].strip()

            location_type = store.xpath(".//preceding::h4//text()")[-1].strip()

            raw_address = (
                store_info.split("ver mapa")[0]
                .split(":")[1]
                .strip()
                .strip("() ")
                .strip()
            )

            formatted_addr = parser.parse_address_intl(raw_address)
            street_address = formatted_addr.street_address_1
            if formatted_addr.street_address_2:
                street_address = street_address + ", " + formatted_addr.street_address_2

            if street_address is not None:
                street_address = street_address.replace("Ste", "Suite")
            city = formatted_addr.city

            if not city:
                city = store.xpath(".//preceding::h2//text()")[-1].strip()

            state = formatted_addr.state
            zip = formatted_addr.postcode

            country_code = "UY"

            phone = (
                store_info.split("Teléfono")[1]
                .split("Email")[0]
                .split("Celular")[0]
                .strip(": ")
                .strip()
            )
            phone = phone.split(" - ")[0].split("int.")[0].strip()

            page_url = search_url

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
