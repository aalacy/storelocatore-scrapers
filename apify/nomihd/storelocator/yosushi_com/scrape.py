# -*- coding: utf-8 -*-
from sgrequests import SgRequests, SgRequestError
from sglogging import sglog
import lxml.html
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import json
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "yosushi.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36",
    "Accept": "application/json",
}


def fetch_data():
    # Your scraper here

    search_url = "https://yosushi.com/restaurants?location=&restaurantTypeFilter=&longitude=&latitude="
    while True:
        stores_req = session.get(search_url, headers=headers)
        stores_sel = lxml.html.fromstring(stores_req.text)

        stores = stores_sel.xpath('//div[@class="restaurant-list"]/div')
        for store in stores:
            location_type = "<MISSING>"

            if (
                "Kiosk"
                in "".join(
                    store.xpath('.//div[@class="restaurant-card__badge"]/text()')
                ).strip()
            ):
                location_type = "Kiosk"

            page_url = (
                "https://yosushi.com"
                + "".join(
                    store.xpath(
                        './/a[@class="btn btn--primary restaurant-card__button"]/@href'
                    )
                ).strip()
            )
            log.info(page_url)
            try:
                store_req = SgRequests.raise_on_err(
                    session.get(page_url, headers=headers)
                )
            except SgRequestError as e:
                log.info(e.status_code)
                continue

            store_sel = lxml.html.fromstring(store_req.text)

            json_str = "".join(
                store_sel.xpath('//script[@type="application/ld+json"]/text()')
            ).strip()
            if len(json_str) <= 0:
                continue
            store_json = json.loads(json_str)

            location_name = store_json["name"]

            locator_domain = website

            street_address = store_json["address"]["streetAddress"]
            city = ""
            if "addressRegion" in store_json["address"]:
                city = store_json["address"]["addressRegion"]
            if city == "":
                if "Chapelfield, Norwich" in street_address:
                    city = "Norwich"
                else:
                    if "," in street_address:
                        city = street_address.split(",")[-1].strip()
                        street_address = ", ".join(
                            street_address.split(",")[:-1]
                        ).strip()

            state = "<MISSING>"
            zip = store_json["address"]["postalCode"]
            country_code = store_json["address"]["addressCountry"]

            phone = store_json["telephone"]

            hours_of_operation = ""
            if "openingHours" in store_json:
                hours_of_operation = "; ".join(store_json["openingHours"])

            if (
                "opening"
                in "".join(store_sel.xpath('//div[@class="hero__status"]/text()'))
                .strip()
                .lower()
            ):
                if (
                    "2021"
                    in "".join(
                        store_sel.xpath('//div[@class="hero__status"]/text()')
                    ).strip()
                ):
                    if len(hours_of_operation) <= 0:
                        continue
            store_number = "<MISSING>"

            latitude = store_json["latitude"]
            longitude = store_json["longitude"]

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

        next_page = stores_sel.xpath(
            '//li[@class="pagination__arrow"]/a[@aria-label="Next Page"]/@href'
        )
        if len(next_page) > 0:
            search_url = "https://yosushi.com" + next_page[0].strip()
        else:
            break


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
