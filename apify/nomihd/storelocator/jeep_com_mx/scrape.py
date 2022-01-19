# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
import json

website = "jeep.com.mx"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "authority": "www.jeep.com.mx",
    "sec-ch-ua": '" Not A;Brand";v="99", "Chromium";v="96", "Google Chrome";v="96"',
    "sec-ch-ua-mobile": "?0",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36",
    "sec-ch-ua-platform": '"Windows"',
    "accept": "*/*",
    "sec-fetch-site": "same-origin",
    "sec-fetch-mode": "cors",
    "sec-fetch-dest": "empty",
    "referer": "https://www.jeep.com.mx/distribuidores/",
    "accept-language": "en-US,en-GB;q=0.9,en;q=0.8",
}


def fetch_data():
    # Your scraper here
    search_url = "https://www.jeep.com.mx/page-data/sq/d/1957112544.json"
    with SgRequests() as session:
        search_res = session.get(search_url, headers=headers)
        json_data = json.loads(search_res.text)["data"]["wordpress"]["dealers"]
        for data in json_data:
            stores = data["items"]["nodes"]
            for store in stores:
                location_type = "<MISSING>"
                page_url = "https://www.jeep.com.mx/distribuidores/" + store["slug"]
                locator_domain = website
                location_name = store["name"]

                street_address = store["address"]
                city = store["city"]
                state = store["state"]
                zip = "<MISSING>"
                country_code = "MX"

                phone = store["tel_test"]
                store_number = store["id"]

                hours_of_operation = "<MISSING>"
                latitude, longitude = store["lat"], store["long"]
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
