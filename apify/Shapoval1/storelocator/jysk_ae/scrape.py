from sgpostal.sgpostal import parse_address_intl
import random
import re
import time

import ssl
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from sgselenium.sgselenium import SgChrome
from sglogging import sglog
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds

ssl._create_default_https_context = ssl._create_unverified_context


website = "https://jysk.ae"
page_url = f"{website}/find-store"
map_url = (
    "https://www.google.com/maps/d/u/0/embed?mid=1b9inCvzuD-jCKmzJV7yfdB20XLWTQcG9"
)
MISSING = SgRecord.MISSING

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

log = sglog.SgLogSetup().get_logger(logger_name=website)


def driver_sleep(driver, time=2):
    try:
        WebDriverWait(driver, time).until(
            EC.presence_of_element_located((By.ID, MISSING))
        )
    except Exception:
        pass


def random_sleep(driver, start=5, limit=3):
    driver_sleep(driver, random.randint(start, start + limit))


def get_phone(Source):
    phone = MISSING

    if Source is None or Source == "":
        return phone

    for match in re.findall(r"[\+\(]?[1-9][0-9 .\-\(\)]{8,}[0-9]", Source):
        phone = match
        return phone
    return phone


def fetch_stores():
    with SgChrome() as driver:
        driver.get(page_url)
        time.sleep(30)
        for frame in driver.find_elements_by_xpath("//iframe"):
            driver.switch_to.frame(frame)
            if "https://maps.gstatic.com/mapfiles/transparent" in driver.page_source:
                buttons = driver.find_elements_by_xpath(
                    '//img[@src="https://maps.gstatic.com/mapfiles/transparent.png"]/parent::*'
                )
                break

        log.debug("Completed page")

        stores = []
        for button in buttons:
            driver.execute_script("arguments[0].click();", button)
            random_sleep(driver)
            element = driver.find_element_by_xpath('//div[text()="name"]/parent::*')
            element = element.find_element_by_xpath(".//parent::*")
            element = element.find_element_by_xpath(".//parent::*")
            text = element.text.strip()
            a = element.find_element_by_xpath(
                './/a[contains(@href, "https://maps.google.com/")]'
            ).get_attribute("href")
            stores.append({"text": text, "a": a})

        fStores = []

        for store in stores:
            googlepage = store["a"].replace("maps.google.com/", "www.google.com/maps")
            driver.get(googlepage)
            time.sleep(30)
            text = store["text"]
            texts = text.split("\n")
            store["location_name"] = texts[1].strip()
            store["raw_address"] = texts[3].strip()
            store["phone"] = get_phone(text)

            current_url = driver.current_url
            try:
                parts = current_url.split("@")[1].split("/")[0].split(",")
                store["latitude"] = parts[0]
                store["longitude"] = parts[1]
            except Exception as e:
                store["latitude"] = MISSING
                store["longitude"] = MISSING
                log.info(f"lat/lng error: {e}")
            fStores.append(store)
    return fStores


def get_js_object(response, varName, noVal=MISSING):
    JSObject = re.findall(f'{varName} = "(.+?)";', response)
    if JSObject is None or len(JSObject) == 0:
        return noVal
    return JSObject[0]


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
    country_code = "UAE"

    for store in stores:
        location_name = store["location_name"]
        raw_address = store["raw_address"]
        location_name = store["location_name"]
        phone = store["phone"]
        latitude = store["latitude"]
        longitude = store["longitude"]
        street_address, city, state, zip_postal = get_address(raw_address)

        yield SgRecord(
            locator_domain="jysk.ae",
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
    with SgWriter(deduper=SgRecordDeduper(RecommendedRecordIds.GeoSpatialId)) as writer:
        for rec in fetch_data():
            writer.write_row(rec)
    end = time.time()
    log.info(f"Scrape took {end-start} seconds.")


if __name__ == "__main__":
    scrape()
