# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html

website = "harvestsupermarkets.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}


def fetch_data():
    # Your scraper here
    search_url = (
        "http://harvestsupermarkets.com/harvest-supermarkets-indiana-locations.html"
    )
    stores_req = session.get(search_url, headers=headers)
    stores_sel = lxml.html.fromstring(stores_req.text)
    stores = stores_sel.xpath('//div[contains(@class,"p7QC-content")]/p')
    for store in stores:
        page_url = search_url
        locator_domain = website
        location_name = "".join(store.xpath("strong//text()")).strip()
        if location_name == "Corporate Headquarters":
            continue

        raw_info = store.xpath("text()")
        raw_list = []
        for raw in raw_info:
            if len("".join(raw).strip()) > 0:
                raw_list.append("".join(raw).strip())

        street_address = raw_list[-4].strip()
        city_state_zip = raw_list[-3].strip()
        city = city_state_zip.split(",")[0].strip()
        state = city_state_zip.split(",")[1].strip().split(" ")[0].strip()
        zip = city_state_zip.split(",")[1].strip().split(" ")[-1].strip()

        country_code = "US"

        store_number = "<MISSING>"
        location_type = "<MISSING>"

        phone = raw_list[-2].strip()
        hours_of_operation = raw_list[-1].strip()

        map_link = "".join(store.xpath("a/@href")).strip()
        latitude = "<MISSING>"
        longitude = "<MISSING>"

        if "/@" in map_link:
            latitude = map_link.split("/@")[1].strip().split(",")[0].strip()
            longitude = map_link.split("/@")[1].strip().split(",")[1]

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
