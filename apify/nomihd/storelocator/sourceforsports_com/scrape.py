# -*- coding: utf-8 -*-
from sgrequests import SgRequests, SgRequestError
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
import json
from sgzip.dynamic import DynamicGeoSearch, SearchableCountries

website = "sourceforsports.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "authority": "www.sourceforsports.com",
    "sec-ch-ua": '" Not A;Brand";v="99", "Chromium";v="98", "Google Chrome";v="98"',
    "accept": "application/json, text/plain, */*",
    "sec-ch-ua-mobile": "?0",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36",
    "sec-ch-ua-platform": '"Windows"',
    "sec-fetch-site": "same-origin",
    "sec-fetch-mode": "cors",
    "sec-fetch-dest": "empty",
    "referer": "https://www.sourceforsports.com/",
    "accept-language": "en-US,en-GB;q=0.9,en;q=0.8",
}


def fetch_data():
    # Your scraper here
    search_url = "https://www.sourceforsports.com/apps/api/stores"

    search = DynamicGeoSearch(
        country_codes=[SearchableCountries.USA],
        expected_search_radius_miles=200,
    )

    for lat, lng in search:
        log.info(f"fetching records for coordinates: {lat},{lng}")
        params = (
            ("coords", f"{lat},{lng}"),
            ("radius", "-1"),
        )
        stores_req = session.get(search_url, headers=headers, params=params)
        if isinstance(stores_req, SgRequestError):
            continue
        stores = json.loads(stores_req.text)
        for store in stores:
            store_number = store["store_number"]
            page_url = (
                "https://www.sourceforsports.com/pages/" + store["landing_page_url"]
            )
            locator_domain = website
            location_name = store["store_name"]

            street_address = store["address"]

            city = store["city"]
            state = store["province"]
            if state:
                state = state.replace("CA-", "").strip()
            zip = store["postal_code"]

            country_code = store["country"]

            phone = store["phone"]

            location_type = "<MISSING>"
            hours = store["opening_hours"]
            hours_list = []
            for index in range(0, len(hours)):
                if index == 0:
                    day = "Sunday:"
                if index == 1:
                    day = "Monday:"
                if index == 2:
                    day = "Tuesday:"
                if index == 3:
                    day = "Wednesday:"
                if index == 4:
                    day = "Thursday:"
                if index == 5:
                    day = "Friday:"
                if index == 6:
                    day = "Saturday:"

                if hours[index]["start"] is None and hours[index]["end"] is None:
                    time = "Closed"
                else:
                    time = hours[index]["start"] + " - " + hours[index]["end"]

                hours_list.append(day + time)

            hours_of_operation = "; ".join(hours_list).strip()

            latitude = store["latitude"]
            longitude = store["longitude"]
            search.found_location_at(lat, lng)

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
