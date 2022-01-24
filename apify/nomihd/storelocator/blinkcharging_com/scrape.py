# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import json
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "blinkcharging.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "Connection": "keep-alive",
    "sec-ch-ua": '" Not;A Brand";v="99", "Google Chrome";v="97", "Chromium";v="97"',
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "X-Requested-With": "XMLHttpRequest",
    "sec-ch-ua-mobile": "?0",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36",
    "sec-ch-ua-platform": '"Windows"',
    "Sec-Fetch-Site": "same-origin",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Dest": "empty",
    "Accept-Language": "en-US,en-GB;q=0.9,en;q=0.8",
}


def fetch_data():
    # Your scraper here
    search_url = (
        "https://blinkcharging.com/wp-content/themes/blinkStrap/blink-api-json.php"
    )
    stores_req = session.get(search_url, headers=headers)
    stores = json.loads(stores_req.text)

    for store in stores:

        page_url = "https://blinkcharging.com/drivers/blink-map/?locale=en"
        store_number = store["id"]
        locator_domain = website

        temp_name = store["name"]

        street_address = store["address1"]
        if len(store["address2"]) > 0:
            if len(street_address) > 0:
                street_address = street_address + ", " + store["address2"]
            else:
                street_address = store["address2"]

        city = store["city"]
        state = store["state"]
        zip = store["zip"]
        country_code = store["country"]
        phone = "<MISSING>"

        units_dict = store["units"]
        for ukey in units_dict.keys():
            units = units_dict[ukey]
            for key in units.keys():
                store_number = units[key]["evseId"]
                location_name = "Unit# " + units[key]["blinkName"] + " " + temp_name
                loc_list = [units[key]["state"]]

                if units[key]["restricted"] is True:
                    loc_list.append("Restricted")

                location_type = ", ".join(loc_list).strip()

                hours_of_operation = "<MISSING>"

                latitude, longitude = units[key]["latitude"], units[key]["longitude"]

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
