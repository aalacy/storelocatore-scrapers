from sgrequests import SgRequests
from sgzip.dynamic import DynamicGeoSearch, SearchableCountries, Grain_8
from sglogging import SgLogSetup
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from typing import Iterable
from sgscrape.pause_resume import SerializableRequest, CrawlState, CrawlStateSingleton
import json
import time


logger = SgLogSetup().get_logger("costa_co_uk__business__costa-express")
DOMAIN = "https://www.costa.co.uk/business/costa-express"
MISSING = SgRecord.MISSING


headers = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.164 Safari/537.36"
}


def record_initial_requests(
    http: SgRequests, state: CrawlState, search: DynamicGeoSearch
) -> bool:
    c = 0
    for lat, lng in search:
        x = round(lat, 4)
        y = round(lng, 4)
        logger.info(f"[{c}] (latitude, longitude) : ({lat, lng}) to be searched")
        url = (
            "http://www.costa.co.uk/api/locations/stores?latitude="
            + str(x)
            + "&longitude="
            + str(y)
            + "&maxrec=500"
        )

        logger.info(url)
        state.push_request(SerializableRequest(url=url))
        c += 1
    return True


def fetch_records(
    http: SgRequests, state: CrawlState, search: DynamicGeoSearch
) -> Iterable[SgRecord]:
    total = 0
    for url_request in state.request_stack_iter():
        r = http.get(url_request.url, headers=headers)
        logger.info(f"Pulling the data from : {url_request.url} ")
        if json.loads(r.content)["stores"]:
            total += len(json.loads(r.content)["stores"])
            for item in json.loads(r.content)["stores"]:
                locator_domain = DOMAIN
                store_number = item["storeNo8Digit"]
                location_type = item["storeType"]

                # Phone
                phone = item["telephone"]
                if phone == "":
                    phone = MISSING

                # Street Address
                add1 = item["storeAddress"]["addressLine1"]
                add = (
                    add1
                    + " "
                    + item["storeAddress"]["addressLine2"]
                    + " "
                    + item["storeAddress"]["addressLine3"]
                )
                add = add.strip()
                street_address = ""
                if add == "" or add is None:
                    street_address = MISSING
                else:
                    street_address = add

                # Location Name
                location_name = item["storeNameExternal"]
                if location_name == "":
                    location_name = location_type

                # City Name
                city = item["storeAddress"]["city"]
                if city == "":
                    city = item["storeAddress"]["addressLine3"]
                if city == "" or city is None:
                    city = MISSING
                if city == MISSING:
                    city = location_name
                if "Belfast" in location_name:
                    city = "Belfast"
                if "Knightswick" in location_name:
                    city = "Knightswick"
                if "Lewes" in location_name:
                    city = "Lewes"
                if "Belper" in location_name:
                    city = "Belper"
                if "Barrow in Furness" in location_name:
                    city = "Barrow in Furness"
                if "Washington" in location_name:
                    city = "Washington"
                if "Purfleet" in add:
                    city = "Purfleet"
                if "Taunton" in location_name:
                    city = "Taunton"
                if "Hempstead Valley" in location_name:
                    city = "Hempstead Valley"
                if "Belfast" in add:
                    city = "Belfast"
                if "Bideford" in location_name:
                    city = "Bideford"

                # State
                state = MISSING

                # Zip Postal
                zip_postal = item["storeAddress"]["postCode"]
                if zip_postal == "" or zip_postal is None:
                    zip_postal = MISSING

                # Country Code
                country_code = "GB"

                # Latitude and Longitude
                latitude = item["latitude"]
                latitude = latitude if latitude else MISSING

                longitude = item["longitude"]
                longitude = longitude if longitude else MISSING

                # page url
                page_url = ""
                if MISSING not in latitude or MISSING not in longitude:
                    page_url = f"https://www.costa.co.uk/locations/store-locator/map?latitude={latitude}&longitude={longitude}"
                else:
                    page_url = "https://www.costa.co.uk/locations/store-locator"

                # Search location found at
                search.found_location_at(latitude, longitude)

                # Hours of Operation
                soh = item["storeOperatingHours"]
                mon = "Mon: " + soh["openMon"] + "-" + soh["closeMon"]
                tue = "Tue: " + soh["openTue"] + "-" + soh["closeTue"]
                wed = "Wed: " + soh["openWed"] + "-" + soh["closeWed"]
                thu = "Thu: " + soh["openThu"] + "-" + soh["closeThu"]
                fri = "Fri: " + soh["openFri"] + "-" + soh["closeFri"]
                sat = "Sat: " + soh["openSat"] + "-" + soh["closeSat"]
                sun = "Sun: " + soh["openSun"] + "-" + soh["closeSun"]
                hours_of_operation = f"{mon}; {tue}; {wed}; {thu}; {fri}; {sat}; {sun}"
                if ":" not in hours_of_operation:
                    hours_of_operation = MISSING

                if (
                    "Mon: -; Tue: -; Wed: -; Thu: -; Fri: -; Sat: -; Sun: -"
                    in hours_of_operation
                ):
                    hours_of_operation = MISSING

                raw_address = str(time.monotonic())
                yield SgRecord(
                    locator_domain=locator_domain,
                    page_url=page_url,
                    location_name=location_name,
                    street_address=street_address,
                    city=city,
                    state=state,
                    zip_postal=zip_postal,
                    country_code=country_code,
                    store_number=store_number,
                    phone=phone,
                    location_type=location_type,
                    latitude=latitude,
                    longitude=longitude,
                    hours_of_operation=hours_of_operation,
                    raw_address=raw_address,
                )
            logger.info(
                f'Number of items found: {len(json.loads(r.content)["stores"])} : Total: {total}'
            )
        else:
            continue


def scrape():
    count = 0
    logger.info("Started")
    state = CrawlStateSingleton.get_instance()
    search = DynamicGeoSearch(
        country_codes=[SearchableCountries.BRITAIN],
        max_search_distance_miles=10,
        max_search_results=500,
        granularity=Grain_8(),
    )

    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.STORE_NUMBER}))
    ) as writer:
        with SgRequests() as http:
            state.get_misc_value(
                "init",
                default_factory=lambda: record_initial_requests(http, state, search),
            )
            for rec in fetch_records(http, state, search):
                writer.write_row(rec)
                count = count + 1

    logger.info(f"No of records being processed: {count}")
    logger.info("Finished")


if __name__ == "__main__":
    scrape()
