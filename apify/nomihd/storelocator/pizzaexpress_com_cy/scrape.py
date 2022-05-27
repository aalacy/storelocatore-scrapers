# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "pizzaexpress.com.cy"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "Accept-Language": "en-US,en;q=0.9,ar;q=0.8",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.75 Safari/537.36",
}


def fetch_data():
    # Your scraper here
    search_url = "https://pizzaexpress.com.cy/find-restaurants/"

    with SgRequests() as session:
        search_res = session.get(search_url, headers=headers)

        search_sel = lxml.html.fromstring(search_res.text)

        stores = search_sel.xpath("//div[h2/span]")

        for store in stores:

            locator_domain = website

            page_url = search_url

            location_name = "".join(store.xpath("./h2//text()")).strip()

            store_info = list(
                filter(
                    str,
                    [x.strip() for x in store.xpath("./div/p[1]//text()")],
                )
            )
            location_type = "<MISSING>"

            raw_address = "".join(store_info)

            street_address = raw_address.split(",")[0].strip()

            city = raw_address.split(",")[-2].strip().split(" ")[-1].strip()

            state = "<MISSING>"
            zip = raw_address.split(",")[-1].strip()

            country_code = "CY"

            store_number = "<MISSING>"

            phone = "".join(store.xpath('.//a[contains(@href,"tel:")]/text()'))
            hours = list(
                filter(
                    str,
                    [x.strip() for x in store.xpath(".//table//text()")],
                )
            )
            hours_of_operation = (
                "; ".join(hours[1:-1]).strip().replace("Dine-in:", "").strip()
            )

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
