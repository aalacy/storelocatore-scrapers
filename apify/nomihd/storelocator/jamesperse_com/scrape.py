# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import json
import lxml.html
from sgscrape import sgpostal as parser

website = "jamesperse.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.114 Safari/537.36",
}


def fetch_data():
    # Your scraper here

    search_url = "https://cdn.shopify.com/s/files/1/0498/5713/4756/t/20/assets/ndnapps-geojson.js"
    search_res = session.get(search_url, headers=headers)

    stores_list = json.loads(
        search_res.text.split("eqfeed_callback(")[1].strip().split("]})")[0].strip()
        + "]}"
    )["features"]

    for store in stores_list:

        page_url = "https://www.jamesperse.com" + store["properties"]["url"]
        locator_domain = website

        location_name = store["properties"]["name"]

        raw_address = store["properties"]["address"]
        formatted_addr = parser.parse_address_intl(raw_address)
        street_address = formatted_addr.street_address_1
        if formatted_addr.street_address_2:
            street_address = street_address + ", " + formatted_addr.street_address_2

        city = formatted_addr.city
        state = formatted_addr.state
        zip = formatted_addr.postcode

        country_code = store["properties"]["country"]

        store_number = "<MISSING>"

        phone = store["properties"]["phone"]

        location_type = store["properties"]["category"]

        hours_of_operation = ""
        hours_list = []
        log.info(page_url)
        store_req = session.get(page_url, headers=headers)
        hours_sel = lxml.html.fromstring(store_req.text)
        hours = hours_sel.xpath("//div[@class='store-info store-times']//table/tr")
        for hour in hours:
            day = "".join(hour.xpath('th[@class="dayname"]/text()')).strip()
            time = "".join(hour.xpath("td/text()")).strip()

            hours_list.append(day + ":" + time)

        hours_of_operation = "; ".join(hours_list).strip()
        latitude = store["properties"]["lat"]
        longitude = store["properties"]["lng"]

        if (
            country_code == "USA"
            or country_code == "Canada"
            or country_code == "United Kingdom"
        ):
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
