# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
import lxml.html

website = "buffalowildwings.ae"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "Upgrade-Insecure-Requests": "1",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36",
}


def get_latlng(map_link):
    if "z/data" in map_link:
        lat_lng = map_link.split("@")[1].split("z/data")[0]
        latitude = lat_lng.split(",")[0].strip()
        longitude = lat_lng.split(",")[1].strip()
    elif "ll=" in map_link:
        lat_lng = map_link.split("ll=")[1].split("&")[0]
        latitude = lat_lng.split(",")[0]
        longitude = lat_lng.split(",")[1]
    elif "!2d" in map_link and "!3d" in map_link:
        latitude = map_link.split("!3d")[1].strip().split("!")[0].strip()
        longitude = map_link.split("!2d")[1].strip().split("!")[0].strip()
    elif "/@" in map_link:
        latitude = map_link.split("/@")[1].split(",")[0].strip()
        longitude = map_link.split("/@")[1].split(",")[1].strip()
    else:
        latitude = "<MISSING>"
        longitude = "<MISSING>"
    return latitude, longitude


def fetch_data():
    # Your scraper here
    search_url = "http://buffalowildwings.ae/store-locations.html"
    search_res = session.get(search_url, headers=headers, verify=False)
    stores_sel = lxml.html.fromstring(search_res.text)
    stores = stores_sel.xpath('//div[@class="card h-100"]')
    for store in stores:
        page_url = search_url
        locator_domain = website

        location_name = "".join(
            store.xpath('.//div[@class="store-title"][1]/text()')
        ).strip()

        raw_address = (
            "".join(store.xpath('.//p[@class="store-text"][1]/text()'))
            .strip()
            .replace(", UAE", "")
            .strip()
            .replace(" UAE", "")
            .strip()
            .split(",")
        )
        street_address = ", ".join(raw_address[:-1]).strip()
        city = "".join(raw_address[-1]).strip()
        state = "<MISSING>"
        zip = "<MISSING>"
        country_code = "AE"

        store_number = "<MISSING>"

        location_type = "<MISSING>"
        phone = "".join(store.xpath('.//p[@class="store-text"][2]/text()')).strip()

        hours_of_operation = "<MISSING>"
        map_link = "".join(
            store.xpath('.//iframe[contains(@src,"maps/embed?")]/@src')
        ).strip()
        latitude, longitude = get_latlng(map_link)

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
        deduper=SgRecordDeduper(record_id=RecommendedRecordIds.PhoneNumberId)
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()
