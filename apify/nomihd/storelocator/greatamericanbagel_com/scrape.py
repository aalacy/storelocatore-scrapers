# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import json
import ast
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "greatamericanbagel.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "authority": "www.greatamericanbagel.com",
    "sec-ch-ua": '"Google Chrome";v="89", "Chromium";v="89", ";Not A Brand";v="99"',
    "accept": "application/json, text/javascript, */*; q=0.01",
    "x-requested-with": "XMLHttpRequest",
    "sec-ch-ua-mobile": "?0",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.114 Safari/537.36",
    "sec-fetch-site": "same-origin",
    "sec-fetch-mode": "cors",
    "sec-fetch-dest": "empty",
    "referer": "https://www.greatamericanbagel.com/location/",
    "accept-language": "en-US,en;q=0.9,ar;q=0.8",
}


def fetch_data():
    # Your scraper here
    api_url = "https://www.greatamericanbagel.com/locations.txt?action=asl_load_stores&nonce=be8db204f6&load_all=1&layout=1"
    api_res = session.get(api_url, headers=headers)
    json_res = json.loads(api_res.text)

    stores_list = json_res
    for store in stores_list:

        if store["country"] not in ["United States", "Canada"]:
            continue

        page_url = "https://www.greatamericanbagel.com/location/"

        locator_domain = website
        location_name = store["title"].strip()
        street_address = store["street"].strip()
        city = store["city"].strip()
        state = store["state"].strip()
        zip = store["postal_code"].strip()
        country = store["country"]
        if country == "United States":
            country_code = "US"
        else:
            country_code = "CA"

        store_number = store["id"]
        phone = store["phone"].strip()

        if store["description"] == "TEMPORARILY CLOSED":
            location_type = "TEMPORARILY CLOSED"
        else:
            location_type = "<MISSING>"

        store_hours = ast.literal_eval(store["open_hours"])
        if store_hours["mon"] in ["0", "1"]:
            hours_of_operation = "<MISSING>"
        else:
            hours_list = []
            for day, timing in store_hours.items():
                hours_list.append(f"{day.upper()}: {timing[0]}")
            hours_of_operation = "; ".join(hours_list)

        latitude = store["lat"]
        longitude = store["lng"]

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
