# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html
import json


website = "junglejims.ca"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "accept": "application/json, text/plain, */*",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Safari/537.36",
}


def fetch_data():
    # Your scraper here
    search_url = "https://junglejims.ca/find-a-restaurant"
    search_res = session.get(search_url, headers=headers)
    search_sel = lxml.html.fromstring(search_res.text)

    store_ids = dict()

    stores = search_sel.xpath('//ul[@class="multi-column-dropdown"]/li')
    for store in stores:
        key = "".join(store.xpath("./a/text()")).strip()  # restautrant name as key
        store_ids[key] = "".join(
            store.xpath("./a/@data-location-id")
        )  # resturant_id as value

    restaurant_list = search_sel.xpath('//div[@class="address-marker"]')

    for restaurant in restaurant_list:

        page_url = search_url
        locator_domain = website

        location_name = "".join(restaurant.xpath(".//h4/text()")).strip()

        street_address = " ".join(restaurant.xpath(".//address/text()")).strip()

        city = location_name
        state = "<MISSING>"
        zip = "<MISSING>"

        country = "CA"
        country_code = country

        store_number = store_ids[location_name]

        phone = "".join(
            restaurant.xpath('.//a[starts-with(@href, "tel:")]/text()')
        ).strip()

        location_type = "<MISSING>"

        hours_of_operation = "<MISSING>"

        latlng = search_res.text.split("var locs = ")[1].split(";")[0].strip()
        lat_lng = json.loads(latlng)

        latitude = lat_lng[store_number][0]
        longitude = lat_lng[store_number][1]
        raw_address = "<MISSING>"

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
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()
