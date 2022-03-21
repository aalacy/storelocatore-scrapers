# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
import json
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgzip.dynamic import DynamicGeoSearch, SearchableCountries
import datetime

website = "diy.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)

headers = {
    "Connection": "keep-alive",
    "sec-ch-ua": '" Not A;Brand";v="99", "Chromium";v="99", "Google Chrome";v="99"',
    "Accept": "application/json, text/plain, */*",
    "Authorization": "Atmosphere atmosphere_app_id=kingfisher-7c4QgmLEROp4PUh0oUebbI94",
    "sec-ch-ua-mobile": "?0",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.51 Safari/537.36",
    "sec-ch-ua-platform": '"Windows"',
    "Origin": "https://diy.com",
    "Sec-Fetch-Site": "cross-site",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Dest": "empty",
    "Referer": "https://diy.com/",
    "Accept-Language": "en-US,en-GB;q=0.9,en;q=0.8",
}


def fetch_data():
    # Your scraper here
    search = DynamicGeoSearch(
        country_codes=[SearchableCountries.BRITAIN],
        expected_search_radius_miles=20,
    )

    search_url = "https://api.kingfisher.com/v1/mobile/stores/BQUK"
    with SgRequests(
        dont_retry_status_codes=([404]),
    ) as session:
        for lat, long in search:

            log.info(f"Coordinates remaining: {search.items_remaining()}")
            params = (
                ("nearLatLong", f"{lat},{long}"),
                ("page/[size/]", "25"),
            )
            stores_req = session.get(search_url, headers=headers, params=params)

            try:
                stores = json.loads(stores_req.text)["data"]
                for store in stores:
                    page_url = "https://diy.com/store/" + store["id"]
                    locator_domain = website

                    store_number = store["id"]
                    store_json = store["attributes"]["store"]
                    location_name = store_json["name"]
                    address = store_json["geoCoordinates"]["address"]["lines"]

                    street_address = (
                        ", ".join(address[:-2]).strip().replace(", ,", ",").strip()
                    )
                    if len(street_address) > 0 and street_address[-1] == ",":
                        street_address = "".join(street_address[:-1]).strip()

                    city = address[-2]
                    state = address[-1]
                    zip = store_json["geoCoordinates"]["postalCode"]

                    country_code = store_json["geoCoordinates"]["countryCode"]

                    phone = store_json["contactPoint"].get("telephone", "<MISSING>")

                    location_type = store_json["brand"] + " " + store_json["storeType"]

                    hour_list = []
                    try:
                        hours = store["attributes"]["openingTimes"]["upcomingDays"]
                        for hour in hours:
                            day = datetime.datetime.strptime(
                                hour["date"], "%Y-%m-%d"
                            ).strftime("%A")
                            time = (
                                hour["openingTimes"]["openingTime"]
                                + "-"
                                + hour["openingTimes"]["closingTime"]
                            )
                            hour_list.append(day + ":" + time)

                    except:
                        pass

                    hours_of_operation = (
                        ";".join(hour_list).strip().replace("Europe/London", "").strip()
                    )

                    latitude = store_json["geoCoordinates"]["latitude"]
                    longitude = store_json["geoCoordinates"]["longitude"]
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

            except:
                pass


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
