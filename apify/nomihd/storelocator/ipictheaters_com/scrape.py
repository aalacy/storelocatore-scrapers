# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import json
import us

website = "ipictheaters.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "authority": "api.ipic.com",
    "sec-ch-ua": '"Chromium";v="88", "Google Chrome";v="88", ";Not A Brand";v="99"',
    "accept": "application/json, text/plain, */*",
    "apikey": "97787D1BD4D34241A6CC6555F6A7827E",
    "sec-ch-ua-mobile": "?0",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.190 Safari/537.36",
    "content-type": "application/json",
    "origin": "https://www.ipic.com",
    "sec-fetch-site": "same-site",
    "sec-fetch-mode": "cors",
    "sec-fetch-dest": "empty",
    "referer": "https://www.ipic.com/",
    "accept-language": "en-US,en-GB;q=0.9,en;q=0.8",
}


def fetch_data():
    # Your scraper here

    search_url = "https://api.ipic.com/iPicAPI2/sites?orderBy=distance&clientLongitude=-74.0178&clientLatitude=40.7662"
    stores_req = session.get(search_url, headers=headers)
    stores = json.loads(stores_req.text)

    for store in stores:
        page_url = (
            "https://www.ipic.com/"
            + store["urlShortName"]
            + "/location?siteId="
            + str(store["siteID"])
        )
        location_type = "<MISSING>"
        locator_domain = website
        location_name = store["name"]

        street_address = store["address"]["address1"]

        city = store["address"]["city"]
        state = store["address"]["stateProvinceAbbr"]
        zip = store["address"]["postalCode"]
        country_code = "<MISSING>"
        if us.states.lookup(state):
            country_code = "US"

        phone = "<MISSING>"
        if "phoneNumber" in store["address"]:
            phone = store["address"]["phoneNumber"]
        hours_of_operation = "<MISSING>"
        store_number = store["siteID"]

        latitude = store["location"]["latitude"]
        longitude = store["location"]["longitude"]

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
