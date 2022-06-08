import random
import ssl
import time
import json
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from sgselenium.sgselenium import SgFirefox
from sglogging import sglog
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds

import os

os.environ[
    "PROXY_URL"
] = "http://groups-RESIDENTIAL,country-pt:{}@proxy.apify.com:8000/"

website = "https://www.fnac.pt"
store_url = "https://www.fnac.pt/localize-loja-fnac/w-4"
MISSING = SgRecord.MISSING

log = sglog.SgLogSetup().get_logger(logger_name=website)


ssl._create_default_https_context = ssl._create_unverified_context


def driver_sleep(driver, time=2):
    try:
        WebDriverWait(driver, time).until(
            EC.presence_of_element_located((By.ID, MISSING))
        )
    except Exception:
        pass


def random_sleep(driver, start=5, limit=3):
    driver_sleep(driver, random.randint(start, start + limit))


def fetch_stores():
    with SgFirefox(block_third_parties=True) as driver:
        driver.get(store_url)
        random_sleep(driver, 20)
        jsontxt = (
            driver.page_source.split('data-stores="')[1].split('" data-zoom=')[0]
        ).replace("&quot;", '"')
        return json.loads(jsontxt)["Store"]

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
    if value is None or len(value) == 0:
        return noVal
    return value


def get_hoo(tt):
    if tt == MISSING or len(tt) == 0:
        return MISSING
    hoo = []
    for tts in tt:
        hoo.append(f'{tts["DayOfWeek"]}: {tts["OpeningPeriods"]}')
    if len(hoo) == 0:
        return MISSING
    return "; ".join(hoo)


def fetch_data():
    stores = fetch_stores()
    log.info(f"Total stores = {len(stores)}")

    state = MISSING
    country_code = "PT"

    for store in stores:
        store_number = get_JSON_object_variable(store, "EAGId")
        page_url = get_JSON_object_variable(store, "Url")
        location_name = get_JSON_object_variable(store, "Name")
        location_type = get_JSON_object_variable(store, "ShopTypeName")
        street_address = get_JSON_object_variable(store, "AddressLine").replace(
            "\n", ", "
        )
        city = get_JSON_object_variable(store, "CityName")
        zip_postal = get_JSON_object_variable(store, "ZipCode")
        phone = "707313435"  # Default phone is actually their helpline so I think its better to include it rather than missing.
        coord = (
            get_JSON_object_variable(store, "Coord")
            .replace("(", "")
            .replace(")", "")
            .split(",")
        )
        latitude = coord[0].strip()
        longitude = coord[1].strip()
        hours_of_operation = get_hoo(get_JSON_object_variable(store, "Timetables"))
        raw_address = f"{street_address}, {city} {zip_postal}".replace(MISSING, "")
        raw_address = " ".join(raw_address.split())
        raw_address = raw_address.replace(", ,", ",").replace(",,", ",")
        if raw_address[len(raw_address) - 1] == ",":
            raw_address = raw_address[:-1]

        yield SgRecord(
            locator_domain="fnac.pt",
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
    with SgWriter(deduper=SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        for rec in fetch_data():
            writer.write_row(rec)
    end = time.time()
    log.info(f"Scrape took {end-start} seconds.")


if __name__ == "__main__":
    scrape()
