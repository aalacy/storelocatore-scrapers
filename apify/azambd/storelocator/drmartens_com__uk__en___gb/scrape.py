from sgpostal.sgpostal import parse_address_intl
import re
import time
import json
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds

website = "https://www.drmartens.com"
page_url = f"{website}/uk/en_gb/store-finder"
json_url = f"{page_url}?q=&longitude=0&latitude=0&page="
MISSING = SgRecord.MISSING


log = sglog.SgLogSetup().get_logger(logger_name=website)


def fetch_stores():
    page = 0
    stores = []
    with SgRequests() as http:
        while True:
            page_val = "" if page == 0 else page
            response = http.get(f"{json_url}{page_val}")
            try:
                stores = stores + json.loads(response.text)["data"]
                log.debug(f"{page}. total stores = {len(stores)}")
            except Exception as e:
                log.info(f"Store Err: {e}")
                break
            page = page + 1
    return stores


def get_phone(Source):
    phone = MISSING

    if Source is None or Source == "":
        return phone

    for match in re.findall(r"[\+\(]?[1-9][0-9 .\-\(\)]{8,}[0-9]", Source):
        phone = match
        return phone
    return phone


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
    if value is None or "" == value:
        return noVal
    return value


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
        log.info(f"Address Err: {e}")
        pass
    return MISSING, MISSING, MISSING, MISSING


def fetch_data():
    stores = fetch_stores()
    log.info(f"Total stores = {len(stores)}")

    store_number = MISSING
    country_code = MISSING
    count = 0
    for store in stores:
        count = count + 1
        location_name = get_JSON_object_variable(store, "displayName")
        location_type = "Store"
        if "Permanently Closed" in location_name:
            location_type = "Permanently Closed"
        latitude = get_JSON_object_variable(store, "latitude")
        longitude = get_JSON_object_variable(store, "longitude")
        phone = get_phone(get_JSON_object_variable(store, "phone"))

        if latitude == "0.0":
            continue

        street_address = (
            get_JSON_object_variable(store, "line1")
            + " "
            + get_JSON_object_variable(store, "line2")
        )
        street_address = street_address.replace(MISSING, "").strip()
        town = get_JSON_object_variable(store, "town")
        zip_postal = get_JSON_object_variable(store, "postalCode")

        raw_address = f"{street_address}, {town} {zip_postal}".replace(MISSING, "")
        raw_address = " ".join(raw_address.split())
        raw_address = raw_address.replace(", ,", ",").replace(",,", ",")
        if raw_address[len(raw_address) - 1] == ",":
            raw_address = raw_address[:-1]
        s1, city, state, z1 = get_address(raw_address)

        towns = town.split(",")
        if city == MISSING and state == MISSING:
            city = towns[0].strip()
            if len(towns) == 2:
                state = towns[1].strip()
        elif city == MISSING and state != town:
            city = towns[0].strip()
        elif state == MISSING and city != town:
            if len(towns) == 2:
                state = towns[1].strip()

        if s1 == z1:
            log.debug(f"{count}. {latitude} {longitude} {location_name}")
        hoo = get_JSON_object_variable(store, "openings")

        hours_of_operation = MISSING
        if hoo != MISSING:
            h1 = []
            for day, hours in hoo.items():
                h1.append(f"{day} {hours}")
            if len(h1) > 0:
                hours_of_operation = " ".join(h1)

        yield SgRecord(
            locator_domain="drmartens.com",
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
    log.info(f"Start Crawl {website} ...")
    start = time.time()
    with SgWriter(deduper=SgRecordDeduper(RecommendedRecordIds.GeoSpatialId)) as writer:
        for rec in fetch_data():
            writer.write_row(rec)
    end = time.time()
    log.info(f"Scrape took {end-start} seconds.")


if __name__ == "__main__":
    scrape()
