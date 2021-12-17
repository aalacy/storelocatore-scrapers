# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "tim-hortons.es"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.114 Safari/537.36",
}


def fetch_data():
    # Your scraper here

    search_url = "https://tim-hortons.es/ubicaciones/"

    with SgRequests() as session:
        search_res = session.get(search_url, headers=headers)
        search_sel = lxml.html.fromstring(search_res.text)
        lat_list = search_res.text.split('"lat":')
        lng_list = search_res.text.split('"lng":')
        stores = search_sel.xpath('//div[@class="large-6 medium-6 cell"]')

        for no, store in enumerate(stores, 1):

            page_url = search_url

            locator_domain = website

            location_name = "".join(store.xpath(".//h4//text()")).strip()

            location_type = "<MISSING>"
            full_address = list(
                filter(
                    str,
                    [
                        x.strip()
                        for x in store.xpath(
                            './/div[@class="small-6 medium-6 cell"][1]//text()'
                        )
                    ],
                )
            )

            raw_address = "<MISSING>"

            street_address = full_address[0].strip()
            city = full_address[-1].strip().split("\t")[0].strip()
            state = "<MISSING>"
            zip = full_address[1].strip()

            country_code = "ES"

            store_number = "<MISSING>"

            phone = full_address[-1].strip().split("\t")[-1].strip()
            if city in phone:
                phone = "MISSING"

            hours = list(
                filter(
                    str,
                    [
                        x.strip()
                        for x in store.xpath(
                            './/div[@class="small-6 medium-6 cell"][2]//text()'
                        )
                    ],
                )
            )
            hours_of_operation = "; ".join(hours).replace("Store Hours:", "").strip()
            latitude, longitude = (
                lat_list[no].split('",')[0].strip().replace('"', "").strip(),
                lng_list[no].split('",')[0].strip().replace('"', "").strip(),
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
        deduper=SgRecordDeduper(record_id=RecommendedRecordIds.GeoSpatialId)
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()
