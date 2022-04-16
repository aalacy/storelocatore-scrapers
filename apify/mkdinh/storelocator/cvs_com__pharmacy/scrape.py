import re
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from sgzip.static import (
    static_coordinate_list,
    SearchableCountries,
)
from sgrequests import SgRequests
from sglogging import SgLogSetup

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds

logger = SgLogSetup().get_logger("cvs_com")


thread_local = threading.local()
base_url = "https://www.cvs.com"

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36",
}


def write_output(data):
    with SgWriter(
        SgRecordDeduper(
            RecommendedRecordIds.StoreNumberId, duplicate_streak_failure_factor=20000
        )
    ) as writer:
        for row in data:
            writer.write_row(row)


def get_session():
    if (
        not hasattr(thread_local, "session")
        or thread_local.request_count > 10
        or thread_local.session_failed
    ):
        thread_local.session = SgRequests()
        thread_local.request_count = 0
        thread_local.session_failed = False

    thread_local.request_count += 1
    return thread_local.session


def fetch_locations(coord):
    locations = []
    session = get_session()

    headers = {
        "x-api-key": "k6DnPo1puMOQmAhSCiRGYvzMYOSFu903",
    }

    params = {
        "latitude": coord[0],
        "longitude": coord[1],
        "searchText": "",
        "filters": "",
        "resultCount": 25,
        "pageNum": 1,
    }

    try:
        response = session.get(
            "https://api.cvshealth.com/locator/v1/stores/search",
            headers=headers,
            params=params,
        )
        data = response.json()
    except:
        logger.error(f"fail to fetch: {coord}")
        return locations

    stores = data.get("storeList", [])

    for store in stores:
        locator_domain = "cvs.com"
        info = store["storeInfo"]

        store_number = info.get("storeId")
        latitude = info.get("latitude")
        longitude = info.get("longitude")
        phone = info.get("phoneNumbers", [])[0]["pharmacy"]

        address = store["address"]
        street_address = address.get("street")
        city = address.get("city")
        state = address.get("state")
        zip_postal = address.get("zip")
        country_code = "US"

        hours_of_operation = get_hours_of_operation(store)

        location_name = f"CVS Pharmacy at {street_address} {city}, {state} {zip_postal}"

        page_url = f'https://www.cvs.com/store-locator/{re.sub(" ", "-", city).lower()}-{state.lower()}-pharmacies/store-details/storeid={store_number}'
        location_type = "Healthhub_Ind"

        locations.append(
            SgRecord(
                locator_domain=locator_domain,
                page_url=page_url,
                location_name=location_name,
                location_type=location_type,
                store_number=store_number,
                street_address=street_address,
                city=city,
                state=state,
                zip_postal=zip_postal,
                country_code=country_code,
                latitude=latitude,
                longitude=longitude,
                phone=phone,
                hours_of_operation=hours_of_operation,
            )
        )

    return locations


def get_hours_of_operation(store):
    departments = store.get("hours")["departments"]
    for department in departments:
        days = department.get("regHours")
        if department["name"] == "pharmacy" and len(days):
            return ", ".join(
                f'{day["weekday"]}: {day["startTime"]}-{day["endTime"]}' for day in days
            )


def scrape():
    with ThreadPoolExecutor() as executor, SgRequests():
        search = static_coordinate_list(radius=25, country_code=SearchableCountries.USA)
        futures = [executor.submit(fetch_locations, coord) for coord in search]

        for future in as_completed(futures):
            for poi in future.result():
                yield poi


if __name__ == "__main__":
    data = scrape()
    write_output(data)
