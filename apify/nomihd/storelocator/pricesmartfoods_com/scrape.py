# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import json


website = "pricesmartfoods.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "authority": "www.pricesmartfoods.com",
    "sec-ch-ua": '" Not;A Brand";v="99", "Google Chrome";v="91", "Chromium";v="91"',
    "accept": "*/*",
    "x-requested-with": "XMLHttpRequest",
    "sec-ch-ua-mobile": "?0",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
    "sec-fetch-site": "same-origin",
    "sec-fetch-mode": "cors",
    "sec-fetch-dest": "empty",
    "accept-language": "en-US,en;q=0.9,ar;q=0.8",
}


def fetch_data():
    # Your scraper here
    search_url = "https://www.pricesmartfoods.com/sm/pickup/rsid/2274/store"
    search_res = session.get(search_url, headers=headers)
    json_str = (
        search_res.text.split('"availablePickupStores":')[1]
        .split(',"availablePlanningStores":')[0]
        .strip()
    )

    json_res = json.loads(json_str)

    stores_list = json_res["items"]

    for store in stores_list:

        store_number = store["retailerStoreId"]
        page_url = (
            f"https://www.pricesmartfoods.com/sm/pickup/rsid/{store_number}/store"
        )

        locator_domain = website

        location_name = store["name"]

        street_address = store["addressLine1"].strip()
        if "addressLine2" in store and store["addressLine2"]:
            street_address = (street_address + ", " + store["addressLine2"]).strip(
                ", ."
            )
        if "addressLine3" in store and store["addressLine3"]:
            street_address = (street_address + ", " + store["addressLine3"]).strip(
                ", ."
            )

        city = store["city"].strip()
        state = store["countyProvinceState"].strip()

        zip = store["postCode"].strip()

        country_code = store["country"].strip()
        phone = store["phone"]

        location_type = "<MISSING>" if store["status"] == "Active" else store["status"]

        hours_of_operation = store["openingHours"]

        latitude = store["location"]["latitude"]
        longitude = store["location"]["longitude"]

        raw_address = "<MISSING>"
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
            raw_address=raw_address,
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
