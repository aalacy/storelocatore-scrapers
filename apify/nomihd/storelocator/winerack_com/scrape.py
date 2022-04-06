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
from sgselenium.sgselenium import SgChrome
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
import ssl

try:
    _create_unverified_https_context = (
        ssl._create_unverified_context
    )  # Legacy Python that doesn't verify HTTPS certificates by default
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context  # Handle target environment that doesn't support HTTPS verification

DOMAIN = "winerack.com"
website = "https://www.winerack.com"
MISSING = SgRecord.MISSING

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

log = sglog.SgLogSetup().get_logger(logger_name=DOMAIN)


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
        hours_of_operation=hoo,
        raw_address=raw_address,
    )


def fetch_data(driver, http, search):
    driver.get(f"{website}/stores")
    random_sleep(driver, 10)
    try:
        driver.find_element_by_xpath(
            "//button[@id='onetrust-accept-btn-handler']"
        ).click()
    except Exception as e:
        log.info(f"Driver failed to find element: {e}")
        pass
    random_sleep(driver, 5)
    driver.find_element(By.CSS_SELECTOR, ".current-selection").click()
    driver.find_element(By.CSS_SELECTOR, ".jsRadius:nth-child(3) > span").click()

    random_sleep(driver, 5)
    inputZip = driver.find_element_by_xpath("//input[contains(@id, 'storesearch')]")
    inputButton = driver.find_element_by_xpath(
        "//button[contains(@class, 'stores__search')]"
    )
    log.debug("Completed initial driver work")

    body = html.fromstring(driver.page_source, "lxml")
    apiKey = body.xpath('//div[@class="stores"]/@data-apikey')[0]
    log.debug(f"apiKey= {apiKey}")

    count = 0
    storeCount = 0
    for zipCode in search:
        count = count + 1
        inputZip.clear()
        driver_sleep(2)
        inputZip.send_keys(zipCode)
        driver_sleep(2)
        log.debug(f"Current input value {inputZip.get_attribute('value')}")
        inputButton.click()
        random_sleep(driver, 5)

        body = html.fromstring(driver.page_source, "lxml")
        storeIds = body.xpath('//div[contains(@class, "stores__item")]/@id')

        log.debug(f"{count}. searching in zip = {zipCode} and stores = {len(storeIds)}")
        for storeId in storeIds:
            storeCount = storeCount + 1
            store = fetch_store(http, apiKey, storeId)
            if store is not None:
                yield store

    log.info(f"Total Stores = {storeCount}")


def scrape():
    log.info(f"Start scrapping {website} ...")
    start = time.time()
    search = DynamicZipSearch(country_codes=[SearchableCountries.CANADA])

    with SgChrome(
        executable_path=ChromeDriverManager().install(), is_headless=True
    ) as driver:
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
                for rec in fetch_data(driver, http, search):
                    writer.write_row(rec)
    end = time.time()
    log.info(f"Scrape took {end-start} seconds.")


if __name__ == "__main__":
    scrape()
