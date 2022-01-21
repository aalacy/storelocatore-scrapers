from sgpostal.sgpostal import parse_address_intl
import os
import json
import random
import ssl
import time
from sgselenium.sgselenium import SgChrome
from sgselenium.sgselenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from sglogging import sglog
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID


try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context


website = "https://www.toalsbet.com"
page_url = f"{website}/shop-locator"
json_url = f"{website}/resources/store_locations.lst"
MISSING = SgRecord.MISSING

file_path = os.path.dirname(os.path.abspath(__file__))

options = webdriver.ChromeOptions()
options.add_argument("--allow-running-insecure-content")
options.add_argument("--ignore-certificate-errors")
options.add_experimental_option("useAutomationExtension", False)
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_argument("--no-proxy-server")
prefs = {"download.default_directory": file_path, "safebrowsing.enabled": "false"}
options.add_experimental_option("prefs", prefs)
log = sglog.SgLogSetup().get_logger(logger_name=website)


def fetch_stores():
    stores = []
    with SgChrome(
        executable_path=ChromeDriverManager().install(),
        is_headless=True,
        chrome_options=options,
    ) as driver:
        driver.get(json_url)
        random_sleep(driver)
        with open("store_locations.lst") as json_file:
            data = json.load(json_file)
            stores = data["storeLocations"]
        os.remove(file_path + "/store_locations.lst")
    return stores


def driver_sleep(driver, time=2):
    try:
        WebDriverWait(driver, time).until(
            EC.presence_of_element_located((By.ID, MISSING))
        )
    except Exception:
        pass


def random_sleep(driver, start=3, limit=3):
    driver_sleep(driver, random.randint(start, start + limit))


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
    store_number = MISSING
    location_type = MISSING
    hours_of_operation = MISSING
    country_code = "UK"
    for store in stores:
        location_name = store["name"]
        raw_address = store["address"]
        street_address, city, state, zip_postal = get_address(raw_address)
        phone = MISSING
        if "tel" in store:
            phone = store["tel"].split(",")[0].strip()
        latitude = store["lat"]
        longitude = store["lon"]

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
        SgRecordDeduper(
            SgRecordID(
                {SgRecord.Headers.LOCATION_NAME, SgRecord.Headers.STREET_ADDRESS}
            )
        )
    ) as writer:
        for rec in fetch_data():
            writer.write_row(rec)
    end = time.time()
    log.info(f"Scrape took {end-start} seconds.")


if __name__ == "__main__":
    scrape()
