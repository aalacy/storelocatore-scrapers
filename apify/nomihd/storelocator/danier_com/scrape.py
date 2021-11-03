# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import json
from bs4 import BeautifulSoup as BS
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "danier.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "Connection": "keep-alive",
    "sec-ch-ua": '"Chromium";v="92", " Not A;Brand";v="99", "Google Chrome";v="92"',
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "sec-ch-ua-mobile": "?0",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36",
    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
    "Origin": "https://danier.com",
    "Sec-Fetch-Site": "cross-site",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Dest": "empty",
    "Referer": "https://danier.com/",
    "Accept-Language": "en-US,en-GB;q=0.9,en;q=0.8",
}


def fetch_data():
    # Your scraper here
    data = {"shopData": "danier-canada.myshopify.com"}

    search_url = "https://storelocator.metizapps.com/stores/storeDataGet"
    stores_req = session.post(search_url, headers=headers, data=data)
    stores = json.loads(stores_req.text)["data"]["result"]
    for store in stores:
        store_number = store["id"]

        page_url = "https://danier.com/a/storelocator"
        locator_domain = website

        location_name = store["storename"]

        street_address = store["address"]
        if len(store["address2"]) > 0:
            street_address = street_address + ", " + store["address2"]

        city = store["cityname"]
        state = store["statename"]
        if state is None or len(state) <= 0:
            continue
        zip = store["zipcode"]

        country_code = store["countryname"]

        phone = store["phone"]

        location_type = "<MISSING>"
        hours_of_operation = BS(store["hour_of_operation"], "lxml").get_text()

        latitude = store["mapLatitude"]
        longitude = store["mapLongitude"]

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
        deduper=SgRecordDeduper(record_id=RecommendedRecordIds.StoreNumberId)
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()
