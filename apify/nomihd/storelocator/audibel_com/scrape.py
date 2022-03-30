# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
import json
from sgzip.dynamic import DynamicZipSearch, SearchableCountries
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "audibel.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()

headers = {
    "Connection": "keep-alive",
    "sec-ch-ua": '" Not A;Brand";v="99", "Chromium";v="99", "Google Chrome";v="99"',
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "X-Requested-With": "XMLHttpRequest",
    "sec-ch-ua-mobile": "?0",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.84 Safari/537.36",
    "sec-ch-ua-platform": '"Windows"',
    "Sec-Fetch-Site": "same-origin",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Dest": "empty",
    "Referer": "https://www.audibel.com/find-a-professional",
    "Accept-Language": "en-US,en-GB;q=0.9,en;q=0.8",
}


def fetch_data():
    # Your scraper here
    search = DynamicZipSearch(
        country_codes=[SearchableCountries.USA],
        expected_search_radius_miles=200,
    )
    for zip_code in search:
        log.info(f"{zip_code} | remaining: {search.items_remaining()}")

        search_url = (
            "https://www.audibel.com/api/dealerservice/Audibel.com/{}/True/False/125"
        ).format(zip_code)
        stores_req = session.get(search_url, headers=headers)
        stores = json.loads(stores_req.text)["Locations"]
        for store_json in stores:
            if store_json["Country"] == "United States":
                page_url = "https://www.audibel.com/find-a-professional"
                locator_domain = website
                location_name = store_json["BusinessName"]
                street_address = store_json["StreetAddress"]
                city_state_zip = store_json["CityStateZip"]
                city = city_state_zip.split(",")[0].strip()
                state = city_state_zip.split(",")[1].strip().split(" ")[0].strip()
                zip = city_state_zip.split(",")[1].strip().split(" ")[1].strip()
                country_code = "US"

                store_number = "<MISSING>"
                phone = store_json["PhoneNumber"]

                location_type = "<MISSING>"
                hours_of_operation = "<MISSING>"

                latitude = store_json["Latitude"]
                longitude = store_json["Longitude"]
                search.found_location_at(latitude, longitude)
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
