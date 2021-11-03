# -*- coding: utf-8 -*-
from sglogging import sglog
import lxml.html
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgselenium import SgChrome
import ssl
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper

try:
    _create_unverified_https_context = (
        ssl._create_unverified_context
    )  # Legacy Python that doesn't verify HTTPS certificates by default
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context  # Handle target environment that doesn't support HTTPS verification

website = "bankofthesierra.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36",
    "Accept": "application/json",
}


def fetch_data():
    # Your scraper here

    search_url = "https://covid19.bankofthesierra.com/locations/"
    with SgChrome() as driver:
        driver.get(search_url)
        stores_sel = lxml.html.fromstring(driver.page_source)
        stores = stores_sel.xpath('//table[@id="locations"]/tbody/tr')
        for store in stores:
            if "".join(store.xpath("@class")).strip() == "county":
                continue

            page_url = "https://covid19.bankofthesierra.com/locations/"
            location_name = "".join(store.xpath("td[1]/strong/text()")).strip()
            location_type = "<MISSING>"
            locator_domain = website
            raw_info = store.xpath("td[1]/text()")
            raw_info_list = []
            for raw in raw_info:
                if len("".join(raw).strip()) > 0:
                    raw_info_list.append("".join(raw).strip())

            phone = raw_info_list[-1]
            street_address = ", ".join(raw_info_list[:-2]).strip()
            city = raw_info_list[-2].strip().split(",")[0].strip()
            state = (
                raw_info_list[-2].strip().split(",")[1].strip().split(" ")[0].strip()
            )
            if " CA" in city:
                city = city.replace(" CA", "").strip()
                state = "CA"
            zipp = (
                raw_info_list[-2].strip().split(",")[1].strip().split(" ")[-1].strip()
            )

            hours_of_operation = "; ".join(store.xpath("td[3]/text()")).strip()

            country_code = "US"
            store_number = "<MISSING>"

            latitude = "<MISSING>"
            longitude = "<MISSING>"

            yield SgRecord(
                locator_domain=locator_domain,
                page_url=page_url,
                location_name=location_name,
                street_address=street_address,
                city=city,
                state=state,
                zip_postal=zipp,
                country_code=country_code,
                store_number=store_number,
                phone=phone,
                location_type=location_type,
                latitude=latitude,
                longitude=longitude,
                hours_of_operation=hours_of_operation,
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
