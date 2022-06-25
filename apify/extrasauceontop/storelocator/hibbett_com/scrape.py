# -*- coding: utf-8 -*-
from sgrequests import SgRequests, SgRequestError
from sglogging import sglog
import json
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgzip.dynamic import SearchableCountries, DynamicGeoSearch
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "citygear.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "authority": "www.hibbett.com",
    "sec-ch-ua": '"Google Chrome";v="95", "Chromium";v="95", ";Not A Brand";v="99"',
    "accept": "application/json, text/javascript, */*; q=0.01",
    "x-requested-with": "XMLHttpRequest",
    "sec-ch-ua-mobile": "?0",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36",
    "sec-ch-ua-platform": '"Windows"',
    "sec-fetch-site": "same-origin",
    "sec-fetch-mode": "cors",
    "sec-fetch-dest": "empty",
    "referer": "https://www.hibbett.com/stores",
    "accept-language": "en-US,en-GB;q=0.9,en;q=0.8",
}


def fetch_data():
    # Your scraper here
    coords = DynamicGeoSearch(
        expected_search_radius_miles=200, country_codes=[SearchableCountries.USA]
    )
    with SgRequests(dont_retry_status_codes=([404])) as session:
        for lat, lng in coords:
            log.info(f"Pulling stores for {lat,lng}")
            url = (
                "https://www.hibbett.com/on/demandware.store/Sites-Hibbett-US-Site/"
                "default/Stores-GetNearestStores?latitude={}&"
                "longitude={}&countryCode=US&distanceUnit=mi&maxdistance=2500000"
            )
            try:
                stores_req = SgRequests.raise_on_err(
                    session.get(
                        url.format(lat, lng),
                        headers=headers,
                    )
                )
                stores = json.loads(stores_req.text.strip())["stores"]
                for store in stores.keys():
                    locator_domain = website
                    location_name = stores[store]["name"]
                    if "hibbett" in location_name.lower():
                        location_name = "Hibbett Sports"
                    street_address = stores[store]["address1"]
                    if len(stores[store]["address2"]) > 0:
                        street_address = (
                            street_address + ", " + stores[store]["address2"]
                        )
                    city = stores[store]["city"]
                    state = stores[store]["stateCode"]
                    zip = stores[store]["postalCode"]
                    country_code = stores[store]["countryCode"]
                    page_url = (
                        "https://www.hibbett.com/storedetails/"
                        + state
                        + "/"
                        + city
                        + "/"
                        + stores[store]["id"]
                    )
                    phone = stores[store]["phone"]
                    store_number = stores[store]["id"]

                    location_type = "<MISSING>"
                    if stores[store]["isOpeningSoon"] is True:
                        location_type = "Opening Soon"

                    if stores[store]["temporarilyClosed"] is True:
                        location_type = "Temporarily Closed"

                    latitude = stores[store]["latitude"]
                    longitude = stores[store]["longitude"]
                    hours_of_operation = (
                        stores[store]["storeHours"].replace("|", " ").strip()
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

            except SgRequestError as e:
                log.error(e.status_code)


def scrape():
    log.info("Started")
    count = 0
    with SgWriter(
        deduper=SgRecordDeduper(
            duplicate_streak_failure_factor=-1,
            record_id=RecommendedRecordIds.StoreNumberId,
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
