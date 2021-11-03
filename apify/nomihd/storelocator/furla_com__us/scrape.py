# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import json

website = "furla.com/us"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "authority": "www.furla.com",
    "sec-ch-ua": '"Chromium";v="88", "Google Chrome";v="88", ";Not A Brand";v="99"',
    "accept": "application/json, text/javascript, */*; q=0.01",
    "x-requested-with": "XMLHttpRequest",
    "sec-ch-ua-mobile": "?0",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36",
    "content-type": "application/text",
    "origin": "https://www.furla.com",
    "sec-fetch-site": "same-origin",
    "sec-fetch-mode": "cors",
    "sec-fetch-dest": "empty",
    "referer": "https://www.furla.com/us/en/eshop/stores",
    "accept-language": "en-US,en-GB;q=0.9,en;q=0.8",
}


def fetch_data():
    # Your scraper here

    search_url = "https://www.furla.com/on/demandware.store/Sites-furla-us-Site/en_US/Stores-GetStores"
    data = '{"center":{"lat":38.555474567327764,"lng":-95.66499999999999},"distance":99999,"filters":{},"types":["country","political"],"address_components":[{"long_name":"United States","short_name":"US","types":["country","political"]}]}'

    stores_req = session.post(search_url, data=data, headers=headers)
    stores = json.loads(stores_req.text)["object"]

    for store in stores:
        store_number = store["ID"]
        page_url = (
            "https://www.furla.com/us/en/eshop/storedetails?StoreID=" + store_number
        )
        location_type = store["storeType"]
        locator_domain = website
        location_name = store["storeName"]

        street_address = store["storeAddress1"]
        if "storeAddress2" in store:
            if store["storeAddress2"] is not None and len(store["storeAddress2"]) > 0:
                street_address = street_address + ", " + store["storeAddress2"]

        city = store["storeCity"]
        state = store["storeRegionState"]
        zip = store["postalCode"]
        country_code = store["countryCodeValue"]
        phone = store["phoneNational"]
        hours_of_operation = ""
        hours_list = []
        for key in store.keys():
            if "storeHours" in key:
                day = key.replace("storeHours", "").strip()
                hours_list.append(day + ":" + store[key])

        hours_of_operation = "; ".join(hours_list).strip()

        if store["storeTemporaryClosed"] is True:
            hours_of_operation = "TemporaryClosed"

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
