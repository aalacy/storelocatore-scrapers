# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "kodakpictures.co.uk"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "Connection": "keep-alive",
    "Accept": "application/xml, text/xml, */*; q=0.01",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.99 Safari/537.36",
    "X-Requested-With": "XMLHttpRequest",
    "Referer": "http://kodakpictures.co.uk/find-a-store.html",
    "Accept-Language": "en-US,en;q=0.9,ar;q=0.8",
}


def fetch_data():
    # Your scraper here
    api_url = "http://kodakpictures.co.uk/locations/all-locations.xml"
    with SgRequests() as session:
        api_res = session.get(api_url, headers=headers)

        api_sel = lxml.html.fromstring(
            api_res.text.split("<?xml")[1].strip().split("?>")[1].strip()
        )

        stores = api_sel.xpath("//marker")

        for store in stores:

            locator_domain = website
            store_number = "<MISSING>"

            page_url = "".join(store.xpath("./@web")).strip()

            location_name = "".join(store.xpath("./@name")).strip()

            location_type = "".join(store.xpath("./@category")).strip()

            phone = "".join(store.xpath("./@phone")).strip()

            raw_address = "<MISSING>"
            street_address = "".join(store.xpath("./@address")).strip()

            street_address = (
                (street_address + "," + "".join(store.xpath("./@address2")).strip())
                .strip(" ,")
                .strip()
            )

            city = "".join(store.xpath("./@city")).strip()

            state = "".join(store.xpath("./@state")).strip()
            zip = "".join(store.xpath("./@postal")).strip()

            country_code = "".join(store.xpath("./@country")).strip()
            if "H.SHACKLETON LTD" == country_code:
                country_code = "United Kingdom"

            hours_of_operation = "".join(store.xpath("./@hours1")).strip()

            latitude, longitude = (
                "".join(store.xpath("./@lat")).strip(),
                "".join(store.xpath("./@lng")).strip(),
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
