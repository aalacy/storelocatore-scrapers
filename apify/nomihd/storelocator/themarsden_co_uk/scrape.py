# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgpostal import sgpostal as parser
import lxml.html
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "themarsden.co.uk"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36",
}


def fetch_data():
    # Your scraper here
    search_url = "https://www.themarsden.co.uk/find-a-branch/"

    with SgRequests() as session:
        search_res = session.get(search_url, headers=headers)

        search_sel = lxml.html.fromstring(search_res.text)
        stores = search_sel.xpath('//ul[@class="accordion branch-list"]/li')

        for no, store in enumerate(stores, 1):

            locator_domain = website

            location_name = "".join(store.xpath("./a//text()")).strip()

            location_type = "<MISSING>"
            page_url = "".join(store.xpath(".//p/a//@href"))

            log.info(page_url)
            store_res = session.get(page_url, headers=headers)
            store_sel = lxml.html.fromstring(store_res.text)

            raw_address = "".join(store.xpath('.//p[contains(@class,"addr")]//text()'))

            formatted_addr = parser.parse_address_intl(raw_address)
            street_address = formatted_addr.street_address_1
            if formatted_addr.street_address_2:
                street_address = street_address + ", " + formatted_addr.street_address_2

            if street_address is not None:
                street_address = (
                    street_address.replace("Ste", "Suite")
                    .replace("Barrowford", "")
                    .strip()
                )

            if street_address and street_address == "20":
                street_address = "20 Teanlowe Shopping Centre"

            city = formatted_addr.city

            state = formatted_addr.state
            zip = formatted_addr.postcode

            country_code = "GB"

            phone = "".join(store.xpath('.//a[contains(@href,"tel")]//text()'))

            hours = list(
                filter(
                    str,
                    [
                        x.strip()
                        for x in store_sel.xpath(
                            '//p[@class="addr-hours__hours"]//text()'
                        )
                    ],
                )
            )
            hours_of_operation = "; ".join(hours).strip().replace(":;", ":").strip()

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
        deduper=SgRecordDeduper(record_id=RecommendedRecordIds.PageUrlId)
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()
