# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import json
import time

website = "bikebarn.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "authority": "www.bikebarn.com",
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
    base = "https://www.bikebarn.com"
    api_url = f"https://www.bikebarn.com/webservices/ajax/storelocator.cfc?method=getGeojson&_={round(time.time()*1000.0)}"
    api_res = session.get(api_url, headers=headers)

    json_res = json.loads(api_res.text)

    stores_list = json_res["features"]

    for store in stores_list:
        store_info = store["properties"]

        page_url = base + store_info["map_templateurl"]

        store_number = store_info["id"]
        locator_domain = website

        location_name = store_info["descriptor"].strip()
        street_address = store_info["address_1"].strip()
        if "address_2" in store_info and store_info["address_2"]:
            street_address = (
                (street_address + ", " + store_info["address_2"]).strip(", ").strip()
            )

        city = store_info["city"].strip()
        state = store_info["state"].strip()

        zip = store_info["zip"].strip()

        country_code = store_info["country"]
        phone = store_info["phone"]
        location_type = "<MISSING>"

        if store_info["hours"]:
            hours = store_info["hours"]

            hours_of_operation = hours.replace("<br />", "; ")

        else:
            hours_of_operation = "<MISSING>"

        latitude = store["geometry"]["coordinates"][1]
        longitude = store["geometry"]["coordinates"][0]

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
