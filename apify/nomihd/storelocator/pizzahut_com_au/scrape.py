# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
import json

website = "pizzahut.com.au"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()

headers = {
    "authority": "store.prod.pizzahutaustralia.com.au",
    "cache-control": "max-age=0",
    "sec-ch-ua": '"Chromium";v="92", " Not A;Brand";v="99", "Google Chrome";v="92"',
    "sec-ch-ua-mobile": "?0",
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "sec-fetch-site": "none",
    "sec-fetch-mode": "navigate",
    "sec-fetch-user": "?1",
    "sec-fetch-dest": "document",
    "accept-language": "en-US,en-GB;q=0.9,en;q=0.8",
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

    search_url = "https://store.prod.pizzahutaustralia.com.au/api/v1/store?includeComingSoon=false"
    stores_req = session.get(search_url, headers=headers)
    stores = json.loads(stores_req.text)
    for store in stores:

        store_name = store["name"].replace(" ", "-")
        page_url = f"https://www.pizzahut.com.au/stores/pizza-hut-{store_name}"
        log.info(page_url)
        api_url = f"https://store.prod.pizzahutaustralia.com.au/api/v1/store/name?name={store['name']}"
        store_req = session.get(api_url, headers=headers)
        if store_req.ok:
            store_json = json.loads(store_req.text)["store"]
            location_name = store_json["name"]
            location_type = store_json["storeType"]
            locator_domain = website

            street_address = store_json["addressLine1"]
            if store_json["addressLine2"]:
                street_address = street_address + ", " + store_json["addressLine2"]
            city = store_json["city"]
            state = store_json["state"]
            zip = store_json["postCode"]

            country_code = store_json["country"]
            store_number = store_json["code"]
            phone = store_json["telephone"]
            hours_list = []
            hours = json.loads(store_req.text)["tradingDays"]

            for hour in hours:
                day = hour["displayDate"]
                time = (
                    hour["tradingHours"][0]["openingTime"]
                    + "-"
                    + hour["tradingHours"][0]["closingTime"]
                )
                hours_list.append(day + ": " + time)

            hours_of_operation = "; ".join(hours_list)

            latitude = "<MISSING>"
            longitude = "<MISSING>"

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
