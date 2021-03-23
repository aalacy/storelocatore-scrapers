# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
import json
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import us
import lxml.html

website = "bmr.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36",
    "Accept": "application/json",
}


def fetch_data():
    # Your scraper here
    search_url = "https://www.bmr.co/en/groupbmr_storelocator/index/getAllStores"
    stores_req = session.get(search_url, headers=headers)
    stores = json.loads(stores_req.text)

    for store in stores:
        page_url = "https://www.bmr.co/en/" + store["rewrite_request_path"]
        locator_domain = website
        location_name = store["name"]
        street_address = store["address"]
        city = store["city"]
        state = store["state"]
        zip = store["zipcode"]

        country_code = "CA"
        if state is not None and us.states.lookup(state):
            country_code = "US"

        store_number = store["StorelocatorId"]
        phone = store["phone"]

        location_type = "<MISSING>"
        if store["is_warehouse"] is True:
            continue

        log.info(page_url)
        store_req = session.get(page_url, headers=headers)
        store_sel = lxml.html.fromstring(store_req.text)

        hours_list = []
        hours = store_sel.xpath('//div[@class="opening-hours"]/li')
        for hour in hours:
            day = "".join(hour.xpath('div[@class="content1"]/text()')).strip()
            time = "".join(hour.xpath('div[@class="content2"]//text()')).strip()
            hours_list.append(day + "" + time)

        hours_of_operation = "; ".join(hours_list).strip()

        latitude = store["latitude"]
        longitude = store["longitude"]

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
