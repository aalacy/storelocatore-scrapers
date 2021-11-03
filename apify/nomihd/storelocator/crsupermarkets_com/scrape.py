# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
import lxml.html
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter

website = "crsupermarkets.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36",
    "Accept": "application/json",
}


def fetch_data():
    # Your scraper here

    search_url = "https://crsupermarkets.com/"
    stores_req = session.get(search_url, headers=headers)
    stores_sel = lxml.html.fromstring(stores_req.text)
    stores = stores_sel.xpath('//div[@class="location-data"]')
    for store in stores:
        page_url = (
            "https://crsupermarkets.com"
            + "".join(store.xpath('h3[@class="site-loc-name"]/a/@href')).strip()
        )
        location_type = "<MISSING>"
        locator_domain = website

        location_name = "".join(
            store.xpath('h3[@class="site-loc-name"]/a/text()')
        ).strip()

        street_address = "".join(
            store.xpath(
                'div[@class="site-loc-address-wrapper"]/div[@class="site-loc-address"]/text()'
            )
        ).strip()
        address_2 = "".join(
            store.xpath(
                'div[@class="site-loc-address-wrapper"]/div[@class="site-loc-address2"]/text()'
            )
        ).strip()
        if len(address_2) > 0:
            street_address = street_address + ", " + address_2

        city_state_zip = "".join(
            store.xpath(
                'div[@class="site-loc-address-wrapper"]/div[@class="site-city-state-zip"]/text()'
            )
        ).strip()
        city = city_state_zip.split(",")[0].strip()
        state = city_state_zip.split(",")[1].strip().split(" ")[0].strip()
        zip = city_state_zip.split(",")[1].strip().split(" ")[-1].strip()

        country_code = "US"

        phone = (
            "".join(store.xpath('div[@class="site-loc-phone"]/text()'))
            .strip()
            .replace("Phone:", "")
            .strip()
        )

        hours_of_operation = (
            "; ".join(store.xpath('div[@class="site-loc-hours"]/text()'))
            .strip()
            .encode("ascii", "replace")
            .decode("utf-8")
            .replace("?", "-")
            .strip()
            .replace("Hours:", "")
            .strip()
        )

        store_number = "".join(store.xpath("@data-location-id")).strip()
        latitude = "".join(store.xpath("@data-lat")).strip()
        longitude = "".join(store.xpath("@data-lon")).strip()

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
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()
