import re
from sgpostal.sgpostal import parse_address_intl
import time
import json
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds

website = "https://www.alcampo.es"
json_url = "https://api.woosmap.com/stores/search?key=woos-761853c3-bb35-3187-98a8-91b1853d08d7&page="
MISSING = SgRecord.MISSING

headers = {
    "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36",
    "accept": "*/*",
    "referer": "https://www.alcampo.es/",
}

session = SgRequests()
log = sglog.SgLogSetup().get_logger(logger_name=website)


def request_with_retries(url):
    return session.get(url, headers=headers)


def fetch_stores():
    page = 0
    stores = []
    while True:
        page = page + 1
        url = f"{json_url}{page}"
        log.info(f"{page}. fetching {url}")
        try:
            response = request_with_retries(url)
            response = json.loads(response.text)
            if "features" in response:
                stores = stores + response["features"]
            else:
                break
        except Exception as e:
            log.info(f"Fail: {e}")
            break
    return stores


def get_var_name(value):
    try:
        return int(value)
    except ValueError:
        pass
    return value


def get_JSON_object(Object, varNames, noVal=MISSING):
    value = noVal
    for varName in varNames.split("."):
        varName = get_var_name(varName)
        try:
            value = Object[varName]
            Object = Object[varName]
        except Exception:
            return noVal
    return value


def get_phone(Source):
    phone = MISSING

    if Source is None or Source == "":
        return phone

    for match in re.findall(r"[\+\(]?[1-9][0-9 .\-\(\)]{8,}[0-9]", Source):
        phone = match
        return phone
    if phone == MISSING:
        for match in re.findall(r"[1-9][0-9 .\-\(\)]{8,}", Source):
            phone = match
            return phone
    return phone


def get_address(raw_address):
    try:
        if raw_address is not None and raw_address != MISSING:
            data = parse_address_intl(raw_address)
            street_address = data.street_address_1
            if data.street_address_2 is not None:
                street_address = street_address + " " + data.street_address_2
            city = data.city
            state = data.state
            zip_postal = data.postcode

            if street_address is None or len(street_address) == 0:
                street_address = MISSING
            if city is None or len(city) == 0:
                city = MISSING
            if state is None or len(state) == 0:
                state = MISSING
            if zip_postal is None or len(zip_postal) == 0:
                zip_postal = MISSING
            return street_address, city, state, zip_postal
    except Exception as e:
        log.info(f"Address Error: {e}")
        pass
    return MISSING, MISSING, MISSING, MISSING


def get_type(properties):
    isGAS = get_JSON_object(properties, "isGAS", 0)
    isCITY = get_JSON_object(properties, "isCITY", 0)
    isMIALC = get_JSON_object(properties, "isMIALC", 0)
    isSUPER = get_JSON_object(properties, "isSUPER", 0)
    isHIPER = get_JSON_object(properties, "isHIPER", 0)

    lType = MISSING
    if isGAS == 1:
        lType = "Gasolinera"
    if isGAS == 0 and isSUPER == 0 and isMIALC == 0 and isCITY == 0:
        lType = "Hipermercado"
    if isGAS == 0 and isHIPER == 0 and isMIALC == 0 and isCITY == 0:
        lType = "Supermercado"
    if isGAS == 0 and isSUPER == 0 and isHIPER == 0 and isCITY == 0:
        lType = "Mi Alcampo"
    if isGAS == 0 and isSUPER == 0 and isMIALC == 0 and isHIPER == 0:
        lType = "Alcampo City"
    return lType


def fetch_data():
    stores = fetch_stores()
    log.info(f"Total stores = {len(stores)}")
    for store in stores:
        properties = get_JSON_object(store, "properties")
        geometry = get_JSON_object(store, "geometry")
        userProperties = get_JSON_object(properties, "user_properties")

        store_number = get_JSON_object(properties, "store_id")
        page_url = f"{website}{get_JSON_object(properties, 'contact.website')}"

        location_type = get_type(userProperties)
        location_name = get_JSON_object(properties, "name")
        if location_type == "Hipermercado" or location_type == "Supermercado":
            location_name = location_name + " - " + location_type
        if location_type == "Gasolinera" and "gasolinera" not in location_name.lower():
            location_name = location_type + " " + location_name

        address = get_JSON_object(properties, "address.lines")[0]
        street_address, city, state, zip_postal = get_address(address)
        city = get_JSON_object(properties, "address.city")
        zip_postal = get_JSON_object(properties, "address.zipcode")

        country_code = get_JSON_object(properties, "address.country_code")
        phone = get_phone(get_JSON_object(properties, "contact.phone"))

        latitude = get_JSON_object(geometry, "coordinates")[0]
        longitude = get_JSON_object(geometry, "coordinates")[1]
        hours_of_operation = get_JSON_object(userProperties, "horario_apertura")

        raw_address = f"{street_address}, {city}, {state} {zip_postal}".replace(
            MISSING, ""
        )
        raw_address = " ".join(raw_address.split())
        raw_address = raw_address.replace(", ,", ",").replace(",,", ",")
        if raw_address[len(raw_address) - 1] == ",":
            raw_address = raw_address[:-1]

        yield SgRecord(
            locator_domain="alcampo.es",
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
