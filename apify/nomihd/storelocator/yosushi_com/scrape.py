# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
import lxml.html
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import json

website = "yosushi.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36",
    "Accept": "application/json",
}


def fetch_data():
    # Your scraper here

    search_url = "https://yosushi.com/restaurants"
    while True:
        stores_req = session.get(search_url, headers=headers)
        stores_sel = lxml.html.fromstring(stores_req.text)

        stores = stores_sel.xpath('//a[@class="content-link__link"]/@href')
        for store_url in stores:
            page_url = "https://yosushi.com" + store_url
            log.info(page_url)
            store_req = session.get(page_url, headers=headers)
            store_sel = lxml.html.fromstring(store_req.text)
            store_json = json.loads(
                "".join(
                    store_sel.xpath('//script[@type="application/ld+json"]/text()')
                ).strip()
            )

            location_type = "<MISSING>"
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
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()
