import time
import json
from lxml import etree
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgzip.dynamic import DynamicGeoSearch, SearchableCountries
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.pause_resume import CrawlStateSingleton
from concurrent.futures import ThreadPoolExecutor


website = "exxon.com"
json_url = "https://www.exxon.com/en/api/v1/Retail/retailstation/GetStationsByBoundingBox?Latitude1={}&Latitude2={}&Longitude1={}&Longitude2={}"
MISSING = SgRecord.MISSING
store_numbers = []
max_workers = 10

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

session = SgRequests()
log = sglog.SgLogSetup().get_logger(logger_name=website)


def request_with_retries(payload):
    lat, lng = payload
    url = json_url.format(lat - 0.5, lat + 1.5, lng - 0.5, lng + 1.5)
    log.info(f"URL: {url}")
    response = session.get(url, headers=headers)
    log.info(f"Response: {response}")
    stores = []
    try:
        data = json.loads(response.text)
    except Exception:
        data = []
    for store in data:
        store_number = store["LocationID"]
        if store_number in store_numbers:
            continue
        store_numbers.append(store_number)
        location_name = store["LocationName"]
        street_address = store["AddressLine1"]
        if store["AddressLine2"]:
            street_address += ", " + store["AddressLine2"]

        if "exxon" in store["BrandingImage"]:
            location_type = "exxon"
        elif "mobil" in store["BrandingImage"]:
            location_type = "mobil"
        else:
            location_type = store["EntityType"]

        city = store["City"]
        state = store["StateProvince"]
        zip_postal = store["PostalCode"]
        country_code = store["Country"]
        phone = store["Telephone"]
        latitude = store["Latitude"]
        longitude = store["Longitude"]
        page_url = f'https://www.exxon.com/en/find-station/exxon-{city.replace(" ", "").lower()}-{state.lower()}-{location_name.lower().replace(" ", "")}-{store_number}'
        page_url = page_url.replace("#", "")

        hoo = ""
        if store["WeeklyOperatingHours"]:
            hoo = etree.HTML(store["WeeklyOperatingHours"]).xpath("//text()")
        hoo = " ".join(hoo)

        raw_address = f"{street_address}, {city}, {state} {zip_postal}".replace(
            MISSING, ""
        )
        raw_address = " ".join(raw_address.split())
        raw_address = raw_address.replace(", ,", ",").replace(",,", ",")
        if raw_address[len(raw_address) - 1] == ",":
            raw_address = raw_address[:-1]

        stores.append(
            {
                "store_number": store_number,
                "page_url": page_url,
                "location_name": location_name,
                "location_type": location_type,
                "street_address": street_address,
                "city": city,
                "zip_postal": zip_postal,
                "state": state,
                "country_code": country_code,
                "phone": phone,
                "latitude": latitude,
                "longitude": longitude,
                "hours_of_operation": hoo,
                "raw_address": raw_address,
            }
        )
    return stores


def fetch_data():
    all_coords = DynamicGeoSearch(
        country_codes=[SearchableCountries.USA],
        expected_search_radius_miles=1,
    )
    count = 0

    while True:
        count = count + 1
        coords = []
        for coord in all_coords:
            coords.append(coord)

            if len(coords) >= max_workers:
                break
        if len(coords) == 0:
            break

        with ThreadPoolExecutor(
            max_workers=max_workers, thread_name_prefix="fetcher"
        ) as executor:
            for stores in executor.map(request_with_retries, coords):
                for store in stores:
                    yield SgRecord(
                        locator_domain=website,
                        store_number=store["store_number"],
                        page_url=store["page_url"],
                        location_name=store["location_name"],
                        location_type=store["location_type"],
                        street_address=store["street_address"],
                        city=store["city"],
                        zip_postal=store["zip_postal"],
                        state=store["state"],
                        country_code=store["country_code"],
                        phone=store["phone"],
                        latitude=store["latitude"],
                        longitude=store["longitude"],
                        hours_of_operation=store["hours_of_operation"],
                        raw_address=store["raw_address"],
                    )

        log.debug(f"{count}. after {count* max_workers} stores = {len(store_numbers)}")


def scrape():
    log.info(f"Start Crawling {website} ...")
    start = time.time()
    CrawlStateSingleton.get_instance().save(override=True)
    with SgWriter(
        deduper=SgRecordDeduper(RecommendedRecordIds.StoreNumberId)
    ) as writer:
        for rec in fetch_data():
            writer.write_row(rec)
    end = time.time()
    log.info(f"Scrape took {end-start} seconds.")


if __name__ == "__main__":
    scrape()
