# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
import json

website = "hemkop.se"
log = sglog.SgLogSetup().get_logger(logger_name=website)

headers = {
    "authority": "www.hemkop.se",
    "sec-ch-ua": '" Not A;Brand";v="99", "Chromium";v="99", "Google Chrome";v="99"',
    "accept": "application/json, text/plain, */*",
    "x-newrelic-id": "VQcCVVdaDhABXFVRDwYAVQ==",
    "sec-ch-ua-mobile": "?0",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.84 Safari/537.36",
    "sec-ch-ua-platform": '"Windows"',
    "sec-fetch-site": "same-origin",
    "sec-fetch-mode": "cors",
    "sec-fetch-dest": "empty",
    "referer": "https://www.hemkop.se/butik-sok",
    "accept-language": "en-US,en-GB;q=0.9,en;q=0.8",
}

params = {
    "online": "false",
}


def fetch_data():
    # Your scraper here
    with SgRequests() as session:
        stores_req = session.get(
            "https://www.hemkop.se/axfood/rest/store", headers=headers, params=params
        )
        stores = json.loads(stores_req.text)
        for store in stores:

            store_number = store["storeId"]
            page_url = f"https://www.hemkop.se/butik/{store_number}"
            locator_domain = website
            location_name = store["name"]
            address = store["address"]
            street_address = address["line1"]
            if "line2" in address and address["line2"] is not None:
                street_address = street_address + ", " + address["line2"]

            city = address.get("town", "<MISSING>")
            state = address.get("region", "<MISSING>")
            zip = address.get("postalCode", "<MISSING>")
            country_code = address["country"]["isocode"]

            phone = address.get("phone", "<MISSING>")
            location_type = ""
            if store["franchiseStore"]:
                location_type = "franchiseStore"

            hours_list = store.get("openingHours", [])
            hours_of_operation = "; ".join(hours_list).strip()

            latitude, longitude = (
                store["geoPoint"]["latitude"],
                store["geoPoint"]["longitude"],
            )

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
