# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import json

website = "wholesaleclub.ca"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36",
    "Accept": "application/json",
}


def fetch_data():
    # Your scraper here

    search_url = (
        "https://www.wholesaleclub.ca/api/pickup-locations?bannerIds=wholesaleclub"
    )
    stores_req = session.get(search_url, headers=headers)
    stores = json.loads(stores_req.text)
    scraped_locations = []
    for store in stores:
        location_type = store["locationType"]
        page_url = (
            "https://www.wholesaleclub.ca/store-locator/details/" + store["storeId"]
        )
        locator_domain = website
        location_name = store["name"]

        street_address = store["address"]["line1"]
        if store["address"]["line2"] is not None and len(store["address"]["line2"]) > 0:
            street_address = street_address + ", " + store["address"]["line2"]
        city = store["address"]["town"]
        state = store["address"]["region"]
        zip = store["address"]["postalCode"]
        country_code = store["address"]["country"]
        store_number = store["storeId"]
        if store_number not in scraped_locations:
            scraped_locations.append(store_number)
            log.info(page_url)
            store_req = session.get(
                "https://www.wholesaleclub.ca/api/pickup-locations/" + store_number,
                headers={
                    "Connection": "keep-alive",
                    "sec-ch-ua": '"Chromium";v="88", "Google Chrome";v="88", ";Not A Brand";v="99"',
                    "Accept": "application/json, text/plain, */*",
                    "Site-Banner": "wholesaleclub",
                    "Accept-Language": "en",
                    "sec-ch-ua-mobile": "?0",
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36",
                    "Content-Type": "application/json;charset=utf-8",
                    "Sec-Fetch-Site": "same-origin",
                    "Sec-Fetch-Mode": "cors",
                    "Sec-Fetch-Dest": "empty",
                },
            )
            store_json = json.loads(store_req.text)
            phone = store_json["storeDetails"]["phoneNumber"]
            hours_of_operation = ""
            hours = store_json["storeDetails"]["storeHours"]
            hours_list = []
            for hour in hours:
                hours_list.append(hour["day"] + ":" + hour["hours"])

            hours_of_operation = "; ".join(hours_list).strip()
            latitude = store["geoPoint"]["latitude"]
            longitude = store["geoPoint"]["longitude"]

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
