# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
import json
import time


website = "heytea.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)

headers = {
    "Connection": "keep-alive",
    "sec-ch-ua": '"Google Chrome";v="95", "Chromium";v="95", ";Not A Brand";v="99"',
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "sec-ch-ua-mobile": "?0",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.54 Safari/537.36",
    "sec-ch-ua-platform": '"Windows"',
    "Origin": "https://www.heytea.com",
    "Sec-Fetch-Site": "same-site",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Dest": "empty",
    "Referer": "https://www.heytea.com/",
    "Accept-Language": "en-US,en;q=0.9,ar;q=0.8",
}

params = (("_", f"{round(time.time() * 1000)}"),)


def fetch_data():
    # Your scraper here

    with SgRequests(dont_retry_status_codes=([404])) as session:
        stores_req = session.get(
            "https://go.heytea.com/api/service-sale/openapi/shop",
            headers=headers,
            params=params,
        )
        search_url = "https://www.heytea.com/indexEn.html#store"
        areas = json.loads(stores_req.text)["data"]

        for area in areas:

            stores = area["store"]

            for store in stores:
                page_url = search_url
                locator_domain = website
                location_name = store["name_en"]

                phone = "<MISSING>"
                raw_address = "<MISSING>"

                street_address = "<MISSING>"

                city = area["area_en"]

                state = "<MISSING>"
                zip = "<MISSING>"
                country_code = "CN"
                if city == "Singapore":
                    country_code = "SG"
                    city = "<MISSING>"

                store_number = "<MISSING>"

                location_type = "<MISSING>"
                hours_of_operation = "<MISSING>"
                latitude = store["dataX"]
                longitude = store["dataY"]

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
        deduper=SgRecordDeduper(record_id=RecommendedRecordIds.GeoSpatialId)
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()
