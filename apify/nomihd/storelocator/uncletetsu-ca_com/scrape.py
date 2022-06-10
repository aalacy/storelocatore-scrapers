# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgpostal import sgpostal as parser


website = "uncletetsu-ca.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "Accept-Language": "en-US,en-GB;q=0.9,en;q=0.8",
    "Connection": "keep-alive",
    "Referer": "http://uncletetsu-ca.com/",
    "Upgrade-Insecure-Requests": "1",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36",
}


def fetch_data():
    # Your scraper here
    with SgRequests(verify_ssl=False) as session:
        search_url = "http://uncletetsu-ca.com/store-location"
        search_res = session.get(search_url, headers=headers)

        search_sel = lxml.html.fromstring(search_res.text)

        stores = search_sel.xpath(
            "//div[@id='canada-box']//div[@class='city_list-box-item']"
        )

        for store in stores:

            page_url = search_url
            locator_domain = website

            raw_address = (
                "".join(store.xpath("p/text()"))
                .strip()
                .replace("Location Address :", "")
                .strip()
            )

            location_name = "".join(store.xpath("h4/text()")).strip()

            formatted_addr = parser.parse_address_intl(raw_address)
            street_address = formatted_addr.street_address_1
            if formatted_addr.street_address_2:
                street_address = street_address + ", " + formatted_addr.street_address_2

            city = formatted_addr.city
            state = formatted_addr.state
            zip = formatted_addr.postcode
            country_code = "CA"

            phone = "<MISSING>"
            hours_of_operation = "<MISSING>"

            store_number = "<MISSING>"

            location_type = "<MISSING>"

            latitude = "<MISSING>"
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
