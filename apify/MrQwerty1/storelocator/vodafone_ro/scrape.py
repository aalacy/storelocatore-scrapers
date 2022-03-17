from sgpostal.sgpostal import parse_address_intl
import time
import json
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID

website = "https://www.vodafone.ro"
page_url = "https://www.vodafone.ro/magazine-vodafone"
js_url = "https://static.vodafone.ro/magazine-vodafone/assets/js/app.js"
MISSING = SgRecord.MISSING

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

session = SgRequests()
log = sglog.SgLogSetup().get_logger(logger_name=website)

keys = [
    "nume",
    "adresa",
    "luni",
    "marti",
    "miercuri",
    "joi",
    "vineri",
    "sambata",
    "duminica",
    "localitate",
    "judet",
    "lo",
    "la",
    "tip_magazin",
    "descriere",
]

days = [
    "luni",
    "marti",
    "miercuri",
    "joi",
    "vineri",
    "sambata",
    "duminica",
]


def request_with_retries(url):
    return session.get(url, headers=headers)


def fetch_stores():
    response = request_with_retries(js_url)
    log.info(f"Response : {response}")
    text = response.text.encode().decode("utf-8-sig")
    data = text.split("m=[{nu")[1]
    data = "[{nu" + data.split("}]")[0] + "}]"
    data = data.replace(" - ", "-")
    for key in keys:
        data = data.replace(f"{key}:", f'"{key}":')
    return json.loads(data)


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
        log.info(f"Address Error: {e}")
        pass
    return MISSING, MISSING, MISSING, MISSING


def fetch_data():
    stores = fetch_stores()
    log.info(f"Total stores = {len(stores)}")

    phone = MISSING
    store_number = MISSING

    for store in stores:
        location_name = get_JSON_object_variable(store, "nume")
        location_type = get_JSON_object_variable(store, "descriere")
        raw_address = (
            get_JSON_object_variable(store, "adresa")
            + " "
            + get_JSON_object_variable(store, "localitate")
            + ""
            + get_JSON_object_variable(store, "judet")
        )
        street_address, city, state, zip_postal = get_address(raw_address)
        city = get_JSON_object_variable(store, "localitate")
        state = get_JSON_object_variable(store, "judet")
        country_code = "RO"
        longitude = str(get_JSON_object_variable(store, "lo"))
        latitude = str(get_JSON_object_variable(store, "la"))

        hoo = []
        for day in days:
            hoo.append(f"{day}: {get_JSON_object_variable(store, day)}")
        hours_of_operation = ";".join(hoo)

        yield SgRecord(
            locator_domain="vodafone.ro",
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
    log.info(f"Start crawling {website} ...")
    start = time.time()
    with SgWriter(
        deduper=SgRecordDeduper(
            SgRecordID({SgRecord.Headers.RAW_ADDRESS, SgRecord.Headers.LOCATION_NAME})
        )
    ) as writer:
        for rec in fetch_data():
            writer.write_row(rec)
    end = time.time()
    log.info(f"Scrape took {end-start} seconds.")


if __name__ == "__main__":
    scrape()
