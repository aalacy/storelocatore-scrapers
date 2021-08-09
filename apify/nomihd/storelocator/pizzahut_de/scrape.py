# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
import json
import lxml.html

website = "pizzahut.de"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()

headers = {
    "Connection": "keep-alive",
    "sec-ch-ua": '"Chromium";v="92", " Not A;Brand";v="99", "Google Chrome";v="92"',
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "X-Requested-With": "XMLHttpRequest",
    "sec-ch-ua-mobile": "?0",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36",
    "Sec-Fetch-Site": "same-origin",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Dest": "empty",
    "Accept-Language": "en-US,en-GB;q=0.9,en;q=0.8",
}


def fetch_data():
    # Your scraper here

    search_url = "https://pizzahut.de/restaurants/getRestaurants"
    stores_req = session.get(search_url, headers=headers)
    stores = json.loads(stores_req.text)
    for store in stores:

        page_url = "https://pizzahut.de/restaurants/" + store["url"]
        location_name = store["name"]
        location_type = "<MISSING>"
        locator_domain = website

        street_address = store["addressStreet"]
        if store["addressStreetNo"]:
            street_address = street_address + " " + store["addressStreetNo"]

        city = store["addressCity"]
        state = store["addressProvince"]
        zip = store["addressPostalCode"]

        country_code = "DE"
        store_number = store["id"]
        phone = store["phoneNo"]
        hours_list = []
        for key in store.keys():
            if key == "openMonTo":
                day = "Mon"
                time = store["openMonFrom"] + " - " + store["openMonTo"]
                hours_list.append(day + ": " + time)
            if key == "openTueTo":
                day = "Tue"
                time = store["openTueFrom"] + " - " + store["openTueTo"]
                hours_list.append(day + ": " + time)
            if key == "openWedTo":
                day = "Wed"
                time = store["openWedFrom"] + " - " + store["openWedTo"]
                hours_list.append(day + ": " + time)
            if key == "openThuTo":
                day = "Thu"
                time = store["openThuFrom"] + " - " + store["openThuTo"]
                hours_list.append(day + ": " + time)
            if key == "openFriTo":
                day = "Fri"
                time = store["openFriFrom"] + " - " + store["openFriTo"]
                hours_list.append(day + ": " + time)
            if key == "openSatTo":
                day = "Sat"
                time = store["openSatFrom"] + " - " + store["openSatTo"]
                hours_list.append(day + ": " + time)
            if key == "openSunTo":
                day = "Sun"
                time = store["openSunFrom"] + " - " + store["openSunTo"]
                hours_list.append(day + ": " + time)

        hours_of_operation = "; ".join(hours_list).strip()

        latitude = store["geoLat"]
        longitude = store["geoLng"]

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
