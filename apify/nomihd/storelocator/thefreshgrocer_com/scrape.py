# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import json

website = "thefreshgrocer.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "authority": "storefrontgateway.brands.wakefern.com",
    "sec-ch-ua": '" Not;A Brand";v="99", "Google Chrome";v="91", "Chromium";v="91"',
    "x-correlation-id": "e8ade013-33d4-49c2-92ea-bcc40a5e7b63",
    "sec-ch-ua-mobile": "?0",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36",
    "accept": "application/json, text/plain, */*",
    "x-shopping-mode": "11111111-1111-1111-1111-111111111111",
    "x-site-host": "https://www.thefreshgrocer.com",
    "customerid": "unknown",
    "origin": "https://www.thefreshgrocer.com",
    "sec-fetch-site": "cross-site",
    "sec-fetch-mode": "cors",
    "sec-fetch-dest": "empty",
    "referer": "https://www.thefreshgrocer.com/",
    "accept-language": "en-US,en-GB;q=0.9,en;q=0.8",
}


def fetch_data():
    # Your scraper here

    search_url = "https://storefrontgateway.brands.wakefern.com/api/near/40.75368539999999/-73.9991637/20000000/10000000/stores"
    stores_req = session.get(search_url, headers=headers)
    stores_list = json.loads(stores_req.text)["items"]

    for store in stores_list:

        page_url = "https://www.thefreshgrocer.com/sm/pickup/rsid/2000/store"
        locator_domain = website

        location_name = store["name"]

        street_address = store["addressLine1"]

        if (
            "addressLine2" in store
            and store["addressLine2"] is not None
            and len(store["addressLine2"]) > 0
        ):
            street_address = street_address + ", " + store["addressLine2"]

        if (
            "addressLine3" in store
            and store["addressLine3"] is not None
            and len(store["addressLine3"]) > 0
        ):
            street_address = street_address + ", " + store["addressLine3"]

        city = store["city"]
        state = store["countyProvinceState"]
        zip = store["postCode"]

        country_code = "US"

        store_number = store["retailerStoreId"]

        phone = store["phone"]

        location_type = "<MISSING>"

        hours_of_operation = store["openingHours"]
        try:
            hours_of_operation = hours_of_operation.split("Senior Shop")[0].strip()
        except:
            pass
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
