# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "timhortonsmx.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.114 Safari/537.36",
}


def fetch_data():
    # Your scraper here

    search_url = "https://timhortonsmx.com/es/sucursales.php"

    with SgRequests() as session:
        search_res = session.get(search_url, headers=headers)
        search_sel = lxml.html.fromstring(search_res.text)

        stores = search_sel.xpath('//div[@class="box"]')

        for _, store in enumerate(stores, 1):

            page_url = search_url

            locator_domain = website

            location_name = "".join(
                store.xpath('.//span[@class="location-city"]//text()')
            ).strip()
            store_info = store.xpath('.//div[@class="div-text"]//text()')

            if len(store_info) == 0:
                location_type = "TEMPORARILY CLOSED"
                phone = "<MISSING>"
                hours_of_operation = "<MISSING>"
                street_address = "<MISSING>"
                city = "<MISSING>"
                state = "<MISSING>"
                zip = "<MISSING>"

            else:
                location_type = "<MISSING>"

                street_address = store_info[0].split(":")[1].strip()
                city = store_info[2].split(":")[1].strip()
                state = "<MISSING>"
                zip = store_info[3].split(":")[1].strip()
                phone = store_info[5].split(":")[1].strip(" -").strip()
                hours_of_operation = store_info[4].split(":")[1].strip()
            country_code = "MX"

            store_number = "".join(
                store.xpath('.//span[@class="location-label"]//text()')
            ).strip()

            raw_address = "<MISSING>"
            latitude, longitude = "".join(store.xpath("./@data-module-lat")), "".join(
                store.xpath("./@data-module-lng")
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
