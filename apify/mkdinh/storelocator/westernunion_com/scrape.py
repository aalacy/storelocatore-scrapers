import threading
from datetime import datetime as dt
from sgrequests import SgRequests
from sglogging import SgLogSetup
from urllib.parse import urljoin
import requests_random_user_agent  # ignore_check # noqa F401
from tenacity import retry, stop_after_attempt
from concurrent.futures import ThreadPoolExecutor, as_completed
from sgzip.static import static_zipcode_list, SearchableCountries
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

logger = SgLogSetup().get_logger("westernunion_com")

thread_local = threading.local()

FIELDS = [
    "locator_domain",
    "page_url",
    "location_name",
    "street_address",
    "city",
    "state",
    "zip",
    "country_code",
    "store_number",
    "phone",
    "location_type",
    "latitude",
    "longitude",
    "hours_of_operation",
]


def write_output(data):
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        for row in data:
            writer.write_row(row)


def fetch(session, postal, country_code, tracker):
    try:
        locations = fetch_pages(session, postal, country_code, [])

        new = []
        for location in locations:
            id = location.get("id")
            if id in tracker:
                continue
            tracker.append(id)

            poi = extract(location)
            new.append(poi)

        return new
    except Exception as e:
        logger.error(e)
        return []


MISSING = "<MISSING>"


def get(entity, key):
    return entity.get(key, MISSING) or MISSING


def get_hours(location):
    hours = get(location, "detail.hours")
    if hours == MISSING:
        return MISSING

    all_days = "00:00-23:59"
    days = [
        "Monday",
        "Tuesday",
        "Wednesday",
        "Thursday",
        "Friday",
        "Saturday",
        "Sunday",
    ]
    return ", ".join(f"{day}: {hours.get(day, all_days)}" for day in days)


def extract(location):
    locator_domain = "westernunion.com"
    location_type = get(location, "type")
    location_name = get(location, "name")
    store_number = get(location, "id")

    url = get(location, "detailsUrl")
    page_url = MISSING if url == MISSING else urljoin("https://westernunion.com", url)

    street_address = get(location, "streetAddress")
    city = get(location, "city")
    state = get(location, "state")
    postal = get(location, "postal")
    country_code = get(location, "country")
    latitude = get(location, "latitude")
    longitude = get(location, "longitude")

    phone = get(location, "phone")
    hours_of_operation = get_hours(location)

    return SgRecord(
        locator_domain=locator_domain,
        location_type=location_type,
        location_name=location_name,
        store_number=store_number,
        page_url=page_url,
        street_address=street_address,
        city=city,
        state=state,
        zip_postal=postal,
        country_code=country_code,
        latitude=latitude,
        longitude=longitude,
        phone=phone,
        hours_of_operation=hours_of_operation,
    )


@retry(stop=stop_after_attempt(3))
def fetch_page(session, country_code, postal, page):
    res = session.get(
        f"https://location.westernunion.com/api/locations?country={country_code}&q={postal}&page={page}"
    ).json()

    results = res.get("results")
    count = res.get("resultCount")

    return count, results


def fetch_pages(session, postal, country_code, locations, page=None):
    count, results = fetch_page(session, country_code, postal, page)
    locations.extend(results)

    if len(locations) < count:
        page = 1 if not page else page + 1
        return fetch_pages(session, postal, country_code, locations, page)

    return locations


def scrape():
    session = SgRequests()
    tracker = []
    us_search = static_zipcode_list(20, SearchableCountries.USA)
    ca_search = static_zipcode_list(30, SearchableCountries.CANADA)
    gb_search = static_zipcode_list(30, SearchableCountries.BRITAIN)

    with ThreadPoolExecutor() as executor:
        futures = []
        futures.extend(
            [
                executor.submit(fetch, session, postal, "US", tracker)
                for postal in us_search
            ]
        )
        futures.extend(
            [
                executor.submit(fetch, session, postal, "CA", tracker)
                for postal in ca_search
            ]
        )
        futures.extend(
            [
                executor.submit(fetch, session, postal, "GB", tracker)
                for postal in gb_search
            ]
        )

        for future in as_completed(futures):
            yield from future.result()


if __name__ == "__main__":
    start = dt.now()
    data = scrape()
    write_output(data)
    logger.info(f"duration: {dt.now() - start}")
