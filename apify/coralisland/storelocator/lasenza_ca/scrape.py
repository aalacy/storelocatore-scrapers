# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import json

website = "lasenza.ca"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()


def fetch_data():
    url = "https://www.lasenza.com/on/demandware.store/Sites-Global-Site/en_US/Stores-GetNearestStores?latitude=43.653226&longitude=-79.38318429999998&countryCode=US&distanceUnit=mi&maxdistance=10000"
    headers = {
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3",
        "accept-encoding": "gzip, deflate, br",
        "upgrade-insecure-requests": "1",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36",
    }
    request = session.get(url, headers=headers)
    store_list = json.loads(request.text)["stores"]
    for key, store in list(store_list.items()):
        if "us" in store["countryCode"].lower() or "ca" in store["countryCode"].lower():

            location_name = store["name"]
            street_address = store["address1"]
            if store["address2"] is not None and len(store["address2"]) > 0:
                street_address = street_address + ", " + store["address2"]
            city = store["city"]
            state = store["stateCode"]
            zip = store["postalCode"]
            country_code = store["countryCode"]
            store_number = key
            page_url = (
                "https://www.lasenza.com/us/store-details/?StoreID=" + store_number
            )
            phone = store["phone"]
            location_type = "La Senza Store"
            latitude = store["latitude"]
            longitude = store["longitude"]
            hours_of_operation = store["storeHours"]
            yield SgRecord(
                locator_domain=website,
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
