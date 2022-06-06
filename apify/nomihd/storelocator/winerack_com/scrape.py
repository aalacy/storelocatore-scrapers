from lxml import html
import time
import json
import random
from sglogging import sglog
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import SgRecordID
from sgzip.dynamic import DynamicZipSearch, SearchableCountries
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgrequests import SgRequests
from sgselenium import SgChrome
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from sgscrape.pause_resume import CrawlStateSingleton
import ssl

ssl._create_default_https_context = ssl._create_unverified_context

website = "https://www.winerack.com"
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


def random_sleep(driver, start=5, limit=6):
    driver_sleep(driver, random.randint(start, start + limit))


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


def get_address_component(arr=[], name=MISSING):
    for value in arr:
        if name in value["types"]:
            return value["short_name"]
    return MISSING


def fetch_store(http, apiKey, store_number):
    api = f"https://maps.googleapis.com/maps/api/place/details/json?reference={store_number}&&sensor=true&key={apiKey}"
    response = json.loads(http.get(api).text)
    if "result" not in response:
        return None

    page_url = f"{website}/stores"
    location_name = "Wine Rack"
    location_type = MISSING

    store = get_JSON_object_variable(response, "result", {})
    address = get_JSON_object_variable(store, "address_components", [])

    street_number = get_address_component(address, "street_number")
    route = get_address_component(address, "route")
    if street_number != MISSING and route != MISSING:
        street_address = street_number + " " + route
    elif street_number != MISSING:
        street_address = street_number
    else:
        street_address = route

    if not street_address or street_address == MISSING:
        if store["formatted_address"]:
            street_address = store["formatted_address"].split(",")[0].strip()

    if street_address:
        street_address = street_address.split(" inside ")[0].strip()
    city = get_address_component(address, "locality")
    state = get_address_component(address, "administrative_area_level_1")
    zip_postal = get_address_component(address, "postal_code")

    phone = get_JSON_object_variable(store, "formatted_phone_number")

    hoo = "; ".join(get_JSON_object_variable(store, "opening_hours.weekday_text", []))
    if len(hoo) == 0:
        hoo = MISSING

    raw_address = f"{street_address}, {city}, {state} {zip_postal}"
    country_code = "CA"

    latitude = get_JSON_object_variable(store, "geometry.location.lat")
    longitude = get_JSON_object_variable(store, "geometry.location.lng")

    return SgRecord(
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
        hours_of_operation=hoo,
        raw_address=raw_address,
    )


def fetch_data(driver, http, zip_codes):
    driver.get(f"{website}/stores")
    random_sleep(driver, 10)
    try:
        driver.find_element(
            by=By.XPATH, value="//button[@id='onetrust-accept-btn-handler']"
        ).click()
    except Exception as e:
        log.info(f"Driver failed to find element: {e}")
        pass
    random_sleep(driver, 5)
    driver.find_element(By.CSS_SELECTOR, ".current-selection").click()
    driver.find_element(By.CSS_SELECTOR, ".jsRadius:nth-child(3) > span").click()

    random_sleep(driver, 5)
    inputZip = driver.find_element(
        by=By.XPATH, value="//input[contains(@id, 'storesearch')]"
    )
    inputButton = driver.find_element(
        by=By.XPATH, value="//button[contains(@class, 'stores__search')]"
    )
    log.debug("Completed initial driver work")

    body = html.fromstring(driver.page_source, "lxml")
    apiKey = body.xpath('//div[@class="stores"]/@data-apikey')[0]
    log.debug(f"apiKey= {apiKey}")

    count = 0
    storeCount = 0
    for zipCode in zip_codes:
        count = count + 1
        inputZip.clear()
        driver_sleep(2)
        inputZip.send_keys(zipCode)
        driver_sleep(2)
        inputButton.click()
        random_sleep(driver, 5)

        body = html.fromstring(driver.page_source, "lxml")
        storeIds = body.xpath('//div[contains(@class, "stores__item")]/@id')
        if len(storeIds) > 0:
            log.info(
                f"{count}. input= {inputZip.get_attribute('value')}; zip= {zipCode}; stores= {len(storeIds)}"
            )
        else:
            log.debug(
                f"{count}. input= {inputZip.get_attribute('value')}; zip= {zipCode}; stores= {len(storeIds)}"
            )
        for storeId in storeIds:
            storeCount = storeCount + 1
            store = fetch_store(http, apiKey, storeId)
            if store is not None:
                yield store

    log.info(f"Total Stores = {storeCount}")


def scrape():
    log.info(f"Start scrapping {website} ...")
    start = time.time()
    CrawlStateSingleton.get_instance().save(override=True)
    search = DynamicZipSearch(
        country_codes=[SearchableCountries.CANADA],
        max_search_results=20,
        max_search_distance_miles=31.0686,
    )

    zip_codes = []
    for zipCode in search:
        zip_codes.append(zipCode)
    log.info(f"Total zip to crawl = {len(zip_codes)}")

    with SgChrome() as driver:
        with SgWriter(
            SgRecordDeduper(
                SgRecordID(
                    {
                        SgRecord.Headers.PAGE_URL,
                        SgRecord.Headers.LOCATION_NAME,
                        SgRecord.Headers.RAW_ADDRESS,
                        SgRecord.Headers.STORE_NUMBER,
                        SgRecord.Headers.PHONE,
                        SgRecord.Headers.LATITUDE,
                        SgRecord.Headers.LONGITUDE,
                        SgRecord.Headers.LOCATION_NAME,
                    }
                )
            )
        ) as writer:
            with SgRequests() as http:
                for rec in fetch_data(driver, http, zip_codes):
                    writer.write_row(rec)
    end = time.time()
    log.info(f"Scrape took {end-start} seconds.")


if __name__ == "__main__":
    scrape()
