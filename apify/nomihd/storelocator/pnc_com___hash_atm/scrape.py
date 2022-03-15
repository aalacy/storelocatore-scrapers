# -*- coding: utf-8 -*-
import time
import random
import datetime
import threading
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

from tenacity import retry, stop_after_attempt
from concurrent.futures import ThreadPoolExecutor, as_completed
from sgselenium import SgChrome
from sgzip.dynamic import DynamicGeoSearch, SearchableCountries

website = "pnc.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
local = threading.local()

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36",
}

id_list = []


def get_session(refresh):
    if refresh or not hasattr(local, "session") or local.count > 10:
        local.session = SgRequests()
        local.count = 0

    local.count += 1
    return local.session


def fetch_locations(url, retry=0):
    try:
        time.sleep(random.randint(1, 3))
        return get_session(retry > 0).get(url, headers=headers).json()
    except Exception:
        if retry < 10:
            return fetch_locations(url, retry + 1)

        log.error(f"Failure to fetch locations for: {url}")
        return None


def fetch_location(url, driver):
    return driver.execute_async_script(
        f"""
        var done = arguments[0]
        return fetch("{url}")
            .then(res => res.json())
            .then(done)
    """
    )


def fetch_records_for(coord):
    lat, lng = coord
    timestamp = str(datetime.datetime.now().timestamp()).split(".")[0].strip()
    search_url = f"https://apps.pnc.com/locator-api/locator/api/v2/location/?t={timestamp}&latitude={lat}&longitude={lng}&radius=100&radiusUnits=mi&branchesOpenNow=false"
    result = fetch_locations(search_url)
    if not result:
        return []

    stores = result["locations"]
    return process_record(stores)


def get_details(store_number, driver):
    url = f"https://apps.pnc.com/locator-api/locator/api/v2/location/details/{store_number}"
    details = fetch_location(url, driver)

    return details, url


@retry(stop=stop_after_attempt(3))
def get_hours(data, details):
    store = data["store"]
    services = details.get("services", []) or []

    store["page_url"] = data["page_url"]
    store["hours_of_operation"] = MISSING

    for service in services:
        if service["service"]["serviceName"] == "Lobby Hours" and service["hours"]:
            hours = []
            for key, value in service["hours"].items():
                if key == "twentyFourHours":
                    continue

                hr = value[0]
                opening = hr["open"]
                closing = hr["close"]
                if opening and closing:
                    hours.append(f"{key}: {opening}-{closing}")
                else:
                    hours.append(f"{key}: Closed")
            store["hours_of_operation"] = ",".join(hours) if len(hours) else MISSING

    return store


def process_record(stores):
    locations = []
    for store in stores:
        store_number = store["locationId"]
        if store["partnerFlag"] == "1" or store_number in id_list:
            continue
        id_list.append(store_number)

        page_url = MISSING
        locator_domain = website
        location_name = store["locationName"]
        street_address = store["address"]["address1"]
        if (
            store["address"]["address2"] is not None
            and len(store["address"]["address2"]) > 0
        ):
            street_address = street_address + ", " + store["address"]["address2"]

        city = store["address"]["city"]
        state = store["address"]["state"]
        zip = store["address"]["zip"]
        country_code = "US"
        latitude = store["address"]["latitude"]
        longitude = store["address"]["longitude"]

        phone = MISSING
        cInfo = store["contactInfo"] or []
        for contact in cInfo:
            if "External Phone" in contact["contactType"]:
                phone = contact["contactInfo"]
                break

        location_type = store["locationType"]["locationTypeDesc"]
        if location_type != "ATM" and store["children"]:
            location_type = "BRANCH AND ATM"

        hours_of_operation = MISSING

        if location_type == "ATM" or location_type == "BRANCH AND ATM":
            record = SgRecord(
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
            ).as_dict()

            locations.append({"store": record, "externalId": store["externalId"]})

    return locations


MISSING = "<MISSING>"
FIELDS = [
    "locator_domain",
    "page_url",
    "location_name",
    "location_type",
    "store_number",
    "street_address",
    "city",
    "state",
    "zip",
    "country_code",
    "latitude",
    "longitude",
    "phone",
    "hours_of_operation",
]


def batch(l, n):
    for i in range(0, len(l), n):
        yield l[i : i + n]


def write_output(data):
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        for row in data:
            writer.write_row(row)


def retry_refetch_hours_error_callback(retry_state):
    return None


@retry(
    stop=stop_after_attempt(5), retry_error_callback=retry_refetch_hours_error_callback
)
def refetch_hours(location):
    with get_session() as driver:
        id = location["externalId"]
        page_url = (
            f"https://apps.pnc.com/locator-api/locator/api/v2/location/details/{id}"
        )
        location["page_url"] = page_url
        details = driver.execute_async_script(
            f"""
            var done = arguments[0]
            fetch("{page_url}")
                .then(res => res.json())
                .then(done)
        """
        )

        if details.get("httpStatusCode"):
            raise Exception()

        return details


def batch_get_hours(locations, driver):
    commands = []

    time.sleep(random.randint(0, 4))
    for location in locations:
        id = location["externalId"]
        page_url = (
            f"https://apps.pnc.com/locator-api/locator/api/v2/location/details/{id}"
        )
        location["page_url"] = page_url
        commands.append(f'fetch("{page_url}").then(res => res.json())')

    result = driver.execute_async_script(
        f"""
        var done = arguments[0]
        Promise.allSettled([{','.join(commands)}])
            .then(results => done({{
                status: 'success',
                data: results
            }}))
            .catch(err => done({{
                status: 'error',
                error: err
            }}))
    """
    )
    if result["status"] == "error":
        log.error(result["error"])

    pois = []
    data = result.get("data")
    if not data:
        return []

    for idx, location in enumerate(locations):
        details = result["data"][idx].get("value")
        if not details:
            log.info(result["data"][idx])
            continue

        if details.get("httpStatusCode"):
            refetched_details = refetch_hours(location)
            if refetched_details:
                details = refetched_details
            else:
                log.error(f'error fetching details: {location["page_url"]}')

        pois.append(get_hours(location, details))

    return pois


def scrape():
    log.info("start")
    locations = []
    coords = DynamicGeoSearch(
        country_codes=[SearchableCountries.USA],
        expected_search_radius_miles=10,
    )

    with ThreadPoolExecutor() as executor:
        futures = [executor.submit(fetch_records_for, coord) for coord in coords]
        for future in as_completed(futures):
            locations.extend(future.result())

        with SgChrome().driver() as driver:
            driver.set_script_timeout(120)
            driver.get("https://pnc.com")
            for chunk in batch(locations, 5):
                pois = batch_get_hours(chunk, driver)
                for poi in pois:
                    yield SgRecord(
                        locator_domain=poi["locator_domain"],
                        page_url=poi["page_url"],
                        location_name=poi["location_name"],
                        street_address=poi["street_address"],
                        city=poi["city"],
                        state=poi["state"],
                        zip_postal=poi["zip"],
                        country_code=poi["country_code"],
                        store_number=poi["store_number"],
                        phone=poi["phone"],
                        location_type=poi["location_type"],
                        latitude=poi["latitude"],
                        longitude=poi["longitude"],
                        hours_of_operation=poi["hours_of_operation"],
                    )
    log.info("end")


if __name__ == "__main__":
    data = scrape()
    write_output(data)
