import time
import json
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgzip.dynamic import DynamicZipSearch, SearchableCountries

website = "https://www.bigotires.com"
store_url = f"{website}/restApi/dp/v1/store/storesByAddress"
MISSING = SgRecord.MISSING

headers = {
    "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:90.0) Gecko/20100101 Firefox/90.0",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
    "Content-Type": "application/json;charset=utf-8",
    "X-Requested-With": "XMLHttpRequest",
    "X-Requested-By": "123",
    "Origin": "https://www.bigotires.com",
    "Connection": "keep-alive",
    "Referer": "https://www.bigotires.com/store-locator",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-origin",
    "TE": "trailers",
}
session = SgRequests()
log = sglog.SgLogSetup().get_logger(logger_name=website)


def request_with_retries(zip_code):
    try:
        payload = {"address": zip_code, "distanceInMiles": 100}
        response = session.post(store_url, headers=headers, data=json.dumps(payload))
        data = json.loads(response.text)
        if "stores" in data["storesType"]:
            return data["storesType"]["stores"]
        return []
    except Exception:
        log.error(f"Can't load from {zip_code}")
        return []


def get_var_name(value):
    try:
        return int(value)
    except ValueError:
        pass
    return value


def get_JSON_object_variable(Object, varNames, noVal=MISSING):
    value = noVal
    for varName in varNames.split("."):
        varName = get_var_name(varName)
        try:
            value = Object[varName]
            Object = Object[varName]
        except Exception:
            return noVal
    if value is None:
        return MISSING
    return value


def get_hoo(data=None):
    if data is None:
        data = []
    hoo = []

    for hour in data:
        days = hour["day"]
        opens = hour["openingHour"]
        closes = hour["closingHour"]
        line = f"{days} {opens} - {closes}"
        hoo.append(line)

    hoo = "; ".join(hoo)
    return hoo


def fetch_data():
    search = DynamicZipSearch(
        country_codes=[SearchableCountries.USA],
        expected_search_radius_miles=100,
    )

    count = 0
    for zip_code in search:
        count = count + 1
        stores = request_with_retries(zip_code)
        log.info(f"{count}. {zip_code} stores = {len(stores)}")

        for store in stores:
            location_name = MISSING
            location_type = MISSING

            address = get_JSON_object_variable(store, "address")

            store_number = get_JSON_object_variable(store, "storeNumber")
            page_url = f"https://www.bigotires.com{get_JSON_object_variable(store, 'storeDetailsUrl')}"
            street_address = get_JSON_object_variable(address, "address1")
            city = get_JSON_object_variable(address, "city")
            zip_postal = get_JSON_object_variable(address, "zipcode")
            state = get_JSON_object_variable(address, "state")
            country_code = "US"
            phone = f"{get_JSON_object_variable(address, 'phoneNumber.areaCode')} {get_JSON_object_variable(address, 'phoneNumber.firstThree')} {get_JSON_object_variable(address, 'phoneNumber.lastFour')}"
            latitude = get_JSON_object_variable(store, "mapCenter.latitude")
            longitude = get_JSON_object_variable(store, "mapCenter.longitude")
            hours_of_operation = get_hoo(
                get_JSON_object_variable(store, "workingHours")
            )

            raw_address = f"{street_address}, {city}, {state} {zip_postal}".replace(
                MISSING, ""
            )
            raw_address = " ".join(raw_address.split())
            raw_address = raw_address.replace(", ,", ",").replace(",,", ",")
            if raw_address[len(raw_address) - 1] == ",":
                raw_address = raw_address[:-1]

            yield SgRecord(
                locator_domain=website,
                store_number=store_number,
                page_url=page_url,
                location_name=location_name,
                location_type=location_type,
                street_address=street_address,
                city=city,
                zip_postal=zip_postal,
                state=state,
                country_code=country_code,
                phone=phone,
                latitude=latitude,
                longitude=longitude,
                hours_of_operation=hours_of_operation,
                raw_address=raw_address,
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
