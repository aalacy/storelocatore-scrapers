# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgpostal import sgpostal as parser
import lxml.html
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "dodge.com.ec"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36",
}


def fetch_data():
    # Your scraper here
    search_url = "https://www.dodge.com.ec/concesionarios/"

    with SgRequests(proxy_country="us") as session:
        search_res = session.get(search_url, headers=headers)

        search_sel = lxml.html.fromstring(search_res.text)
        stores = search_sel.xpath('//div[@class="direcciones"]/div')

        for store in stores:

            locator_domain = website

            location_type = "<MISSING>"

            store_info = list(
                filter(str, [x.strip() for x in store.xpath(".//p//text()")])
            )

            location_name = store_info[0].strip()

            raw_address = ", ".join(store_info[1:]).strip().split("ono:")[0].strip()

            formatted_addr = parser.parse_address_intl(raw_address)
            street_address = formatted_addr.street_address_1
            if formatted_addr.street_address_2:
                street_address = street_address + ", " + formatted_addr.street_address_2

            if street_address is not None:
                street_address = street_address.replace("Ste", "Suite")
            city = formatted_addr.city
            if not city:
                city = "".join(store.xpath(".//h3//text()")).strip()
            state = formatted_addr.state
            zip = formatted_addr.postcode

            country_code = "EC"

            phone = (
                " ".join(store_info[1:])
                .strip()
                .split("ono:")[1]
                .split("Ventas:")[0]
                .split("Taller:")[0]
                .strip()
            )

            page_url = search_url

            hours_of_operation = (
                " ".join(store_info[1:])
                .strip()
                .split("Ventas:")[1]
                .split("Taller:")[0]
                .strip()
            )

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
        deduper=SgRecordDeduper(
            SgRecordID(
                {
                    SgRecord.Headers.RAW_ADDRESS,
                    SgRecord.Headers.LOCATION_NAME,
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
