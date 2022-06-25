import time
import json
from lxml import etree
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds

website = "exxon.com"
json_url = "https://www.exxon.com/en/api/locator/Locations?Latitude1={}&Latitude2={}&Longitude1={}&Longitude2={}&DataSource=RetailGasStations&Country=US"
MISSING = SgRecord.MISSING

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

session = SgRequests()
log = sglog.SgLogSetup().get_logger(logger_name=website)

MAX_COUNT = 250
FLOATING_POINT = 15


def request_with_retries(lat1, lat2, lng1, lng2):
    url = json_url.format(lat1, lat2, lng1, lng2)
    response = session.get(url, headers=headers)
    stores = []
    for store in json.loads(response.text):
        store_number = store["LocationID"]

        location_name = store["LocationName"]
        street_address = store["AddressLine1"]
        if store["AddressLine2"]:
            street_address += ", " + store["AddressLine2"]

        location_type = store["EntityType"]
        city = store["City"]
        state = store["StateProvince"]
        zip_postal = store["PostalCode"]
        country_code = store["Country"]
        phone = store["Telephone"]
        latitude = store["Latitude"]
        longitude = store["Longitude"]
        page_url = f'https://www.exxon.com/en/find-station/exxon-{city.replace(" ", "").lower()}-{state.lower()}-{location_name.lower().replace(" ", "")}-{store_number}'

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


def fetch_stores(lat1, lat2, lng1, lng2, count=0):
    stores = request_with_retries(lat1, lat2, lng1, lng2)
    totalFound = len(stores)
    log.info(f"{count}. [{lat1},{lat2},{lng1},{lng2}] total stores = {len(stores)}")
    if totalFound < MAX_COUNT or (lat1 == lat2 and lng1 == lng2):
        return stores
    lat3 = str(round((float(lat1) + float(lat2)) / 2, FLOATING_POINT))
    lng3 = str(round((float(lng1) + float(lng2)) / 2, FLOATING_POINT))

    bottom_left = fetch_stores(lat1, lat3, lng1, lng3, count + 1)
    bottom_right = fetch_stores(lat1, lat3, lng3, lng2, count + 1)
    top_left = fetch_stores(lat3, lat2, lng1, lng3, count + 1)
    top_right = fetch_stores(lat3, lat2, lng3, lng2, count + 1)
    log.debug(f"After finishing {count} total stores = {len(stores)}")

    return bottom_left + bottom_right + top_left + top_right


def fetch_data():
    stores = fetch_stores(
        "19.50139", "64.85694", "-161.75583", "-68.01197"
    )  # US geospatial bounds
    log.info(f"Total stores = {len(stores)}")
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
    return []


def scrape():
    log.info(f"Start scrapping {website} ...")
    start = time.time()
    with SgWriter(
        deduper=SgRecordDeduper(RecommendedRecordIds.StoreNumberId)
    ) as writer:
        for rec in fetch_data():
            writer.write_row(rec)
    end = time.time()
    log.info(f"Scrape took {end-start} seconds.")


if __name__ == "__main__":
    scrape()
