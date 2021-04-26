# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
import lxml.html
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter

website = "oldspaghettifactory.ca"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36",
    "Accept": "application/json",
}


def fetch_data():
    # Your scraper here

    search_url = "http://www.oldspaghettifactory.ca/#locations"
    stores_req = session.get(search_url, headers=headers)
    stores_sel = lxml.html.fromstring(stores_req.text)
    stores = stores_sel.xpath('//footer/a[contains(text(),"View More")]/@href')
    for store_url in stores:
        page_url = store_url
        location_type = "<MISSING>"
        locator_domain = website
        log.info(page_url)
        store_req = session.get(page_url, headers=headers)
        store_sel = lxml.html.fromstring(store_req.text)
        location_name = "".join(
            store_sel.xpath('//header/div[@class="title"]/text()')
        ).strip()

        street_address = "".join(
            store_sel.xpath('//div[@class="address"]/text()')
        ).strip()
        state = "".join(store_sel.xpath('//div[@class="province"]/text()')).strip()
        city_zip = "".join(store_sel.xpath('//div[@class="city"]/text()')).strip()
        city = city_zip.split(",")[0].strip()
        zip = city_zip.split(",")[1].strip()
        country_code = "CA"

        phone = (
            "".join(store_sel.xpath('//div[@class="phone"]/a/text()'))
            .strip()
            .replace("Phone:", "")
            .strip()
        )

        hours_of_operation = (
            "; ".join(store_sel.xpath('//div[@class="hours"]/p/text()'))
            .strip()
            .encode("ascii", "replace")
            .decode("utf-8")
            .replace("?", " ")
            .strip()
        )
        store_number = "<MISSING>"

        latitude = "<MISSING>"
        longitude = "<MISSING>"

        map_link = "".join(store_sel.xpath('//a[@class="map-link"]/@href')).strip()
        if len(map_link) > 0:
            if "/@" in map_link:
                latitude = map_link.split("/@")[1].strip().split(",")[0].strip()
                longitude = map_link.split("/@")[1].strip().split(",")[1].strip()

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
