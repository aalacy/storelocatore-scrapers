# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgzip.dynamic import DynamicGeoSearch, SearchableCountries
import json
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "sunglasshut.com/uk"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "authority": "www.sunglasshut.com",
    "sec-ch-ua": '" Not A;Brand";v="99", "Chromium";v="96", "Google Chrome";v="96"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.93 Safari/537.36",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "sec-fetch-site": "none",
    "sec-fetch-mode": "navigate",
    "sec-fetch-user": "?1",
    "sec-fetch-dest": "document",
    "accept-language": "en-US,en-GB;q=0.9,en;q=0.8",
    "referer": "https://www.sunglasshut.com/uk/sunglasses/store-locations/map?location=London%2C%20UK",
}

referUrl = "https://www.sunglasshut.com/uk/sunglasses/store-locations/map?location=London%2C%20UK"


def fetch_data():
    # Your scraper here
    search = DynamicGeoSearch(
        country_codes=[SearchableCountries.BRITAIN], expected_search_radius_miles=100
    )

    with SgRequests(dont_retry_status_codes=([404])) as session:
        session.get(referUrl, headers=headers)

        for lat, long in search:
            log.info(f"{(lat, long)}")

            params = (
                ("latitude", lat),
                ("longitude", long),
                ("radius", "2000"),
            )

            stores_req = session.get(
                "https://www.sunglasshut.com/AjaxSGHFindPhysicalStoreLocations",
                params=params,
            )
            log.info(f"Status Code: {stores_req}")
            stores = json.loads(stores_req.text)["locationDetails"]
            for store in stores:
                if store["countryCode"] == "GB":
                    page_url = "<MISSING>"
                    locator_domain = website
                    location_name = store["displayAddress"]
                    street_address = store["address"]

                    city = store["city"]
                    state = "<MISSING>"
                    zip = store["zip"]
                    country_code = store["countryCode"]

                    phone = store["phone"]
                    location_type = "<MISSING>"

                    store_number = store["id"]
                    hours = store["hours"]
                    hours_list = []
                    for hour in hours:
                        day = hour["day"]
                        time = ""
                        if len(hour["open"]) <= 0 and len(hour["close"]) <= 0:
                            time = "Closed"
                        else:
                            time = hour["open"] + "-" + hour["close"]

                        hours_list.append(day + ":" + time)

                    hours_of_operation = (
                        "; ".join(hours_list)
                        .strip()
                        .encode("ascii", "replace")
                        .decode("utf-8")
                        .replace("?", "-")
                        .strip()
                    )

                    latitude = store["latitude"]
                    longitude = store["longitude"]
                    if latitude == "0.00000":
                        latitude = "<MISSING>"
                    if longitude == "0.00000":
                        longitude = "<MISSING>"

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
        deduper=SgRecordDeduper(
            record_id=RecommendedRecordIds.StoreNumberId,
            duplicate_streak_failure_factor=-1,
        )
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()
