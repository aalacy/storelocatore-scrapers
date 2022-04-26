# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import json
import lxml.html
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "boxlunch.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "authority": "www.boxlunch.com",
    "cache-control": "max-age=0",
    "sec-ch-ua": '"Google Chrome";v="89", "Chromium";v="89", ";Not A Brand";v="99"',
    "sec-ch-ua-mobile": "?0",
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Safari/537.36",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "sec-fetch-site": "none",
    "sec-fetch-mode": "navigate",
    "sec-fetch-user": "?1",
    "sec-fetch-dest": "document",
    "accept-language": "en-US,en-GB;q=0.9,en;q=0.8",
}


def fetch_data():
    # Your scraper here
    search_url = "https://www.boxlunch.com/on/demandware.store/Sites-boxlunch-Site/default/Stores-FindStores?showMap=false&radius=50000&stateCode=&lat=40.75368539999999&long=-73.9991637&postalCode=10001"
    stores_req = session.get(search_url, headers=headers)
    stores = json.loads("".join(stores_req.text).strip())["stores"]

    for store in stores:
        locator_domain = website
        store_number = store["ID"]
        page_url = "https://www.boxlunch.com/stores-details?StoreID=" + store_number
        location_name = store["name"]
        if "coming soon" in location_name.lower():
            continue
        street_address = store["address1"]
        if (
            "address2" in store
            and store["address2"] is not None
            and len(store["address2"]) > 0
        ):
            street_address = street_address + ", " + store["address2"]
        city = store["city"]
        state = store["stateCode"]
        zip = store["postalCode"]

        country_code = store["countryCode"]
        phone = store["phone"]

        location_type = "<MISSING>"

        hours_list = []

        if (
            "storeHours" in store
            and store["storeHours"] is not None
            and len(store["storeHours"]) > 0
        ):
            hours_sel = lxml.html.fromstring(store["storeHours"])
            hours = hours_sel.xpath('//div[@class="hours-row"]')
            for hour in hours:
                day = "".join(
                    hour.xpath('span[@class="store-hours-day"]/text()')
                ).strip()
                time = "".join(
                    hour.xpath('span[@class="store-hours-time"]/text()')
                ).strip()
                hours_list.append(day + ":" + time)

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
