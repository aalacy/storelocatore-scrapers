# -*- coding: utf-8 -*-
import csv
import threading
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgzip.dynamic import SearchableCountries
from sgzip.static import static_coordinate_list
from tenacity import retry, stop_after_attempt
import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

website = "pnc.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
local = threading.local()

headers = {
    "authority": "apps.pnc.com",
    "sec-ch-ua": '" Not A;Brand";v="99", "Chromium";v="90", "Google Chrome";v="90"',
    "accept": "application/json, text/plain, */*",
    "sec-ch-ua-mobile": "?0",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36",
    "sec-fetch-site": "same-origin",
    "sec-fetch-mode": "cors",
    "sec-fetch-dest": "empty",
    "referer": "https://apps.pnc.com/locator/search",
    "accept-language": "en-US,en-GB;q=0.9,en;q=0.8",
}

id_list = []


def get_session():
    if not hasattr(local, "session") or local.count > 5:
        local.session = SgRequests()
        local.count = 0

    local.count += 1
    return local.session


def retry_error_callback(retry_state):
    coord = retry_state.args[0]
    log.error(f"Failure to fetch locations for: {coord}")
    return []


@retry(stop=stop_after_attempt(3), retry_error_callback=retry_error_callback)
def fetch_locations(base_url, coord):
    timestamp = str(datetime.datetime.now().timestamp()).split(".")[0].strip()
    url = base_url.format(timestamp, coord[0], coord[1])

    return get_session().get(url, headers=headers, timeout=15).json()


def fetch_records_for(coord):
    search_url = "https://apps.pnc.com/locator-api/locator/api/v2/location/?t={}&latitude={}&longitude={}&radius=100&radiusUnits=mi&branchesOpenNow=false"
    result = fetch_locations(search_url, coord)
    stores = result["locations"]
    return process_record(stores)


def retry_fetch_phone_error_callback(retry_state):
    id = retry_state.args[0]
    log.error(f"Failure to fetch phone for: {id}")
    return None


@retry(
    stop=stop_after_attempt(3), retry_error_callback=retry_fetch_phone_error_callback
)
def fetch_phone(id):
    timestamp = str(datetime.datetime.now().timestamp()).split(".")[0].strip()
    url = f"https://apps.pnc.com/locator-api/locator/api/v2/location/details/{id}?t={timestamp}"

    store_json = (
        get_session().get(url.format(timestamp), headers=headers, timeout=15).json()
    )
    cInfo = store_json["contactInfo"] or []

    for contact in cInfo:
        if "External Phone" in contact["contactType"]:
            return contact["contactInfo"]


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
        latitude = store["address"]["latitude"]
        longitude = store["address"]["longitude"]

        if location_type == "ATM" or location_type == "BRANCH AND ATM":
            if phone == MISSING:
                externalId = store["externalId"]
                phone = fetch_phone(externalId)

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

            locations.append([record[field] for field in FIELDS])

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


def write_output(data):
    with open("data.csv", mode="w") as output_file:
        writer = csv.writer(
            output_file, delimiter=",", quotechar='"', quoting=csv.QUOTE_ALL
        )
        writer.writerow(FIELDS)
        for rows in data:
            writer.writerows(rows)


def scrape():
    coords = static_coordinate_list(radius=10, country_code=SearchableCountries.USA)

    with ThreadPoolExecutor() as executor:
        futures = [executor.submit(fetch_records_for, coord) for coord in coords]
        for future in as_completed(futures):
            locations = future.result()
            yield locations


if __name__ == "__main__":
    data = scrape()
    write_output(data)
