# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
import lxml.html
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter

website = "sellersbros.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36",
    "Accept": "application/json",
}


def fetch_data():
    # Your scraper here

    search_url = "https://sellersbros.com/locations/"
    stores_req = session.get(search_url, headers=headers)
    stores_sel = lxml.html.fromstring(stores_req.text)
    stores = stores_sel.xpath('//div[@class="location-module"]/div')
    for store in stores:
        page_url = "".join(
            store.xpath('div[@class="location-more"]/div[2]/a/@href')
        ).strip()
        location_type = "<MISSING>"
        locator_domain = website
        log.info(page_url)
        store_req = session.get(page_url, headers=headers)
        store_sel = lxml.html.fromstring(store_req.text)

        location_name = "".join(
            store.xpath(
                'div[@class="module-location"]/div[@class="location-title"]/text()'
            )
        ).strip()

        street_address = "".join(
            store.xpath('div[@class="location-more"]/div[1]/text()')
        ).strip()
        city_state_zip = "".join(
            store.xpath('div[@class="location-more"]/div[2]/text()')
        ).strip()
        city = city_state_zip.split(",")[0].strip()
        state = city_state_zip.split(",")[1].strip().split(" ")[0].strip()
        zip = city_state_zip.split(",")[1].strip().split(" ")[-1].strip()

        country_code = "US"

        phone = "".join(
            store.xpath(
                'div[@class="location-more"]/div[@class="location-phone"]/text()'
            )
        ).strip()

        hours_of_operation = (
            "".join(
                store.xpath(
                    'div[@class="module-location"]/div[@class="open-days"]/text()'
                )
            )
            .strip()
            .encode("ascii", "replace")
            .decode("utf-8")
            .replace("?", "-")
            .strip()
        )
        store_number = "<MISSING>"
        if "#" in location_name:
            store_number = location_name.split("#")[1].strip()

        latitude = "<MISSING>"
        longitude = "<MISSING>"

        map_link = "".join(
            store_sel.xpath('//iframe[contains(@src,"maps/embed?")]/@src')
        ).strip()

        if len(map_link) > 0:
            latitude = map_link.split("!3d")[1].strip().split("!")[0].strip()
            longitude = map_link.split("!2d")[1].strip().split("!")[0].strip()
        else:
            map_link = "".join(
                store_sel.xpath('//div[@class="map-i"]/iframe/@src')
            ).strip()
            if "sll=" in map_link:
                latitude = map_link.split("sll=")[1].strip().split(",")[0].strip()
                longitude = (
                    map_link.split("sll=")[1]
                    .strip()
                    .split(",")[1]
                    .strip()
                    .split("&")[0]
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
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()
