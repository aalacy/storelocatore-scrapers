# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "sweetbloomcoffee.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36",
}


def fetch_data():
    # Your scraper here
    search_url = "https://sweetbloomcoffee.com/pages/locations"

    with SgRequests() as session:
        search_res = session.get(search_url, headers=headers)

        search_sel = lxml.html.fromstring(search_res.text)

        stores = search_sel.xpath("//div[@class='container py-4 py-sm-5 py-md-7']")

        for no, store in enumerate(stores, 1):

            locator_domain = website
            store_number = "<MISSING>"

            page_url = search_url

            location_name = "".join(
                store.xpath(".//h2[@class='h1 pb-2']//text()")
            ).strip()

            location_type = "".join(
                store.xpath(".//h2[@class='display-1']//text()")
            ).strip()

            store_info = list(
                filter(
                    str,
                    [
                        x.strip()
                        for x in store.xpath(".//p/a[contains(@href,'http')]//text()")
                    ],
                )
            )

            phone = "".join(store.xpath('.//a[contains(@href,"tel:")]/text()')).strip()
            hours_of_operation = "; ".join(store.xpath(".//p[not(a)]/text()")).strip()
            street_address = store_info[0]
            city = store_info[-1].strip().split(",")[0].strip()
            state = store_info[-1].strip().split(",")[-1].strip().split(" ")[0].strip()
            zip = store_info[-1].strip().split(",")[-1].strip().split(" ")[-1].strip()

            country_code = "US"
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
            )


def scrape():
    log.info("Started")
    count = 0
    with SgWriter(
        deduper=SgRecordDeduper(SgRecordID({SgRecord.Headers.LOCATION_NAME}))
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()
