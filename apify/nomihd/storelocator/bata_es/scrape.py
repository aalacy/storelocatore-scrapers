# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
import json

website = "bata.es"
log = sglog.SgLogSetup().get_logger(logger_name=website)

headers = {
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "Accept-Language": "en-US,en-GB;q=0.9,en;q=0.8",
    "Connection": "keep-alive",
    "Referer": "https://www.bata.es/store-locator",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-origin",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.63 Safari/537.36",
    "X-Requested-With": "XMLHttpRequest",
    "sec-ch-ua": '" Not A;Brand";v="99", "Chromium";v="102", "Google Chrome";v="102"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
}


def fetch_data():
    # Your scraper here
    page_index = 1
    with SgRequests() as session:
        while True:
            log.info(f"fetching data from pageNo:{page_index}")
            params_dict = {
                "omitCoords": 1,
                "filters": {
                    "distance": {"value": 5000},
                    "search_lat": {"value": 43.3},
                    "search_lng": {"value": 13},
                },
                "page": page_index,
            }
            params = {
                "params": json.dumps(params_dict),
                "_": "1654082462497",
            }
            stores_req = session.get(
                "https://www.bata.es/store-locator-stores",
                params=params,
                headers=headers,
            )
            stores = json.loads(stores_req.text)["stores"]["list"]
            if len(stores) <= 0:
                break

            for store in stores:
                locator_domain = website
                store_number = store["storenumber"]
                page_url = f"https://www.bata.es/store-detail/{store_number}"
                location_name = store["storename"]

                street_address = store["street"]
                city = store["city"]
                state = "<MISSING>"
                zip = store["zip"]
                country_code = "ES"
                phone = "<MISSING>"
                hours_of_operation = "<MISSING>"

                props = store["other"]["properties"]
                for key in props.keys():
                    if props[key]["en_US.UTF-8"]["description"] == "Phone number":
                        phone = props[key]["en_US.UTF-8"]["value"]

                    if props[key]["en_US.UTF-8"]["description"] == "Open hours":
                        hours_of_operation = props[key]["en_US.UTF-8"]["value"]

                location_type = "<MISSING>"
                if store["is_franchise"] != 0:
                    location_type = "Franchise"

                latitude, longitude = (
                    store["latitude"],
                    store["longitude"],
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

            page_index = page_index + 1


def scrape():
    log.info("Started")
    count = 0
    with SgWriter(
        deduper=SgRecordDeduper(record_id=RecommendedRecordIds.PageUrlId)
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()
