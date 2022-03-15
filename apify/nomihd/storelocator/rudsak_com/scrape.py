# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import json


website = "rudsak.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "authority": "rudsak.com",
    "sec-ch-ua": '" Not A;Brand";v="99", "Chromium";v="90", "Google Chrome";v="90"',
    "sec-ch-ua-mobile": "?0",
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "sec-fetch-site": "none",
    "sec-fetch-mode": "navigate",
    "sec-fetch-user": "?1",
    "sec-fetch-dest": "document",
    "accept-language": "en-US,en;q=0.9,ar;q=0.8",
}


def fetch_data():
    # Your scraper here
    api_url = "https://stores.boldapps.net/front-end/get_surrounding_stores.php?shop=rudsakofficialsite.myshopify.com&latitude=57.328745&longitude=-96.678314&max_distance=0&limit=100&calc_distance=0"
    api_res = session.get(api_url, headers=headers)

    json_res = json.loads(api_res.text)

    store_list = json_res["stores"]

    for store in store_list:

        page_url = "https://rudsak.com/apps/store-locator"
        locator_domain = website

        location_name = store["name"]

        street_address = store["address"]
        if "address2" in store and store["address2"]:
            street_address = (
                (street_address + "," + store["address2"]).strip(", ").strip()
            )

        city = store["city"]
        state = store["prov_state"]
        zip = store["postal_zip"]

        country_code = store["country"]

        store_number = store["store_id"]

        phone = store["phone"]

        location_type = "<MISSING>"

        hours_of_operation = (
            store["hours"]
            .replace("  ", " ")
            .replace("\n", "; ")
            .replace("  ", " ")
            .replace("\r", " ")
            .replace("  ", " ")
            .replace("\t", " ")
            .replace("  ", " ")
            .replace("DAY", "DAY:")
            .replace(" ;", ";")
            .strip()
        )
        if "TEMP CLOSE" in hours_of_operation:
            location_type = "Temporarily Closed"

        latitude, longitude = store["lat"], store["lng"]
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
