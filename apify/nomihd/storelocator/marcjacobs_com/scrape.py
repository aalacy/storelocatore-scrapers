# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import json
import lxml.html
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "marcjacobs.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "authority": "www.marcjacobs.com",
    "sec-ch-ua": '" Not;A Brand";v="99", "Google Chrome";v="91", "Chromium";v="91"',
    "sec-ch-ua-mobile": "?0",
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "sec-fetch-site": "none",
    "sec-fetch-mode": "navigate",
    "sec-fetch-user": "?1",
    "sec-fetch-dest": "document",
    "accept-language": "en-US,en-GB;q=0.9,en;q=0.8",
}


def fetch_data():
    # Your scraper here
    search_url = "https://www.marcjacobs.com/on/demandware.store/Sites-mjsfra-Site/default/Stores-FindStores?showMap=false&radius=20000&refineBy=&postalCode=&countryCode=&radius=20000&boutiques=on"
    stores_req = session.get(search_url, headers=headers)
    stores = json.loads(stores_req.text)["stores"]
    for store in stores:

        locator_domain = website

        location_name = store["name"]

        street_address = store["address1"]
        if store["address2"] is not None and len(store["address2"]) > 0:
            street_address = street_address + ", " + store["address2"]

        city = store["city"]
        state = ""
        if "stateCode" in store:
            state = store["stateCode"]

        zip = store["postalCode"]

        country_code = store["countryCode"]

        store_number = store["ID"]

        phone = (
            store.get("phone", "<MISSING>")
            .split("; Cell:")[0]
            .strip()
            .replace("Phone:", "")
            .strip()
        )

        location_type = "<MISSING>"
        if "MARC JACOBS" in location_name:
            location_type = "boutique"

        page_url = "https://www.marcjacobs.com/on/demandware.store/Sites-mjsfra-Site/default/Stores-Details?StoreID={}&format=ajax".format(
            store_number
        )
        log.info(page_url)
        store_req = session.get(page_url, headers=headers)
        store_sel = lxml.html.fromstring(store_req.text)
        hours_of_operation = (
            "; ".join(store_sel.xpath('//time[@itemprop="openingHours"]/div/text()'))
            .strip()
            .replace("\n", "")
            .strip()
        )

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
