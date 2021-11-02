import time
import json
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds

DOMAIN = "alexandani.com"
website = "https://www.alexandani.com"
page_url = "https://www.alexandani.com/pages/store-locator"
json_url = "https://stockist.co/api/v1/u6591/locations/all.js"
MISSING = SgRecord.MISSING

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

session = SgRequests()
log = sglog.SgLogSetup().get_logger(logger_name=website)


def request_with_retries(url):
    return session.get(url, headers=headers)


def fetch_stores():
    response = request_with_retries(json_url)
    stores = json.loads(response.text)
    return stores


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
            return noVal
    return value


def get_hoo(data):
    hoo = []
    for d in data:
        hoo.append(f"{d['name']}: {d['value']}")
    if len(hoo) == 0:
        return MISSING
    return "; ".join(hoo)


def fetch_data():
    stores = fetch_stores()
    log.info(f"Total stores = {len(stores)}")
    for store in stores:

        store_number = str(get_JSON_object_variable(store, "id"))
        location_name = get_JSON_object_variable(store, "name")
        street_address = (
            get_JSON_object_variable(store, "address_line_1")
            + " "
            + get_JSON_object_variable(store, "address_line_2")
        )
        street_address = street_address.replace(MISSING, "").strip()
        city = get_JSON_object_variable(store, "city")
        zip_postal = get_JSON_object_variable(store, "postal_code")
        state = get_JSON_object_variable(store, "state")
        country_code = get_JSON_object_variable(store, "country")
        if country_code == "United States":
            country_code = "US"
        phone = get_JSON_object_variable(store, "phone")
        latitude = get_JSON_object_variable(store, "latitude")
        longitude = get_JSON_object_variable(store, "longitude")
        location_type = get_JSON_object_variable(store, "filters.0.name")
        hours_of_operation = get_hoo(get_JSON_object_variable(store, "custom_fields"))

        raw_address = f"{street_address}, {city}, {state} {zip_postal}".replace(
            MISSING, ""
        )
        raw_address = " ".join(raw_address.split())
        raw_address = raw_address.replace(", ,", ",").replace(",,", ",")
        if raw_address[len(raw_address) - 1] == ",":
            raw_address = raw_address[:-1]

        yield SgRecord(
            locator_domain=DOMAIN,
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
    log.info(f"Start Crawling {website} ...")
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
