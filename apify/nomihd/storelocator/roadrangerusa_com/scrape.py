# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "roadrangerusa.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36",
    "Accept": "application/json",
}


def fetch_data():
    # Your scraper here
    search_url = "https://www.roadrangerusa.com/locations-amenities/find-a-road-ranger"
    with SgRequests() as session:
        stores_req = session.get(search_url, headers=headers)
        stores_sel = lxml.html.fromstring(stores_req.text)
        stores = stores_sel.xpath('//li[@class="store-location-row"]')
        for store in stores:
            page_url = search_url

            locator_domain = website
            location_name = (
                "".join(
                    store.xpath('.//h4[@class="store-location-teaser__address"]/text()')
                )
                .strip()
                .replace("20 Frontage Rd.", "20 Frontage Rd,")
                .strip()
            )

            address = "".join(location_name).split("(")[0]
            if len(address.split(",")) == 3:
                street_address = address.split(",")[0].strip()
                city = address.split(",")[1].strip()
                state = address.split(",")[2].strip()
            elif len(address.split(",")) == 2:
                street_address = address.split(",")[0].strip()
                city = " ".join(
                    address.split(",")[1].strip().rsplit(" ", 1)[:-1]
                ).strip()
                state = address.split(",")[1].strip().rsplit(" ", 1)[-1].strip()

            if len(city) <= 0:
                if "Monahans" in street_address:
                    street_address = street_address.replace("Monahans", "").strip()
                    city = "Monahans"

            zip = "<MISSING>"
            if len(state.split(" ")) > 1:
                zip = state.split(" ")[-1].strip()
                state = state.split(" ")[0].strip()

            country_code = "US"

            store_number = "<MISSING>"
            phone = "".join(store.xpath('.//a[contains(@href,"tel:")]/text()')).strip()
            location_type = "<MISSING>"
            hours_of_operation = (
                "".join(store.xpath('.//div[@class="location_hours"]/text()'))
                .strip()
                .replace("STORE HOURS:", "")
                .strip()
                .replace("LIMITED HOURS:", "")
                .strip()
            )
            latitude = (
                "".join(
                    store.xpath(
                        './/div[./span[@class="fa-solid fa-map-location-dot"]]/text()'
                    )
                )
                .strip()
                .strip()
                .replace("Coordinates:", "")
                .strip()
                .split(",")[0]
                .strip()
            )
            longitude = (
                "".join(
                    store.xpath(
                        './/div[./span[@class="fa-solid fa-map-location-dot"]]/text()'
                    )
                )
                .strip()
                .strip()
                .replace("Coordinates:", "")
                .strip()
                .split(",")[1]
                .strip()
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
