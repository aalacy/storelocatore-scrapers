import time
import json
import re

from sglogging import sglog
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgzip.dynamic import DynamicZipSearch, SearchableCountries, Grain_4

from sgselenium.sgselenium import SgChrome
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

import ssl

try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context

website = "https://www.lmcu.org"

MISSING = "<MISSING>"

log = sglog.SgLogSetup().get_logger(logger_name=website)

search = DynamicZipSearch(
    country_codes=[SearchableCountries.USA],
    max_search_distance_miles=None,
    max_search_results=None,
    granularity=Grain_4(),
)


def initiateDriver(url, class_name, driver=None):
    if driver is not None:
        driver.quit()

    user_agent = (
        "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:78.0) Gecko/20100101 Firefox/78.0"
    )
    x = 0
    while True:
        x = x + 1
        try:
            driver = SgChrome(
                executable_path=ChromeDriverManager().install(),
                user_agent=user_agent,
                is_headless=True,
            ).driver()
            driver.get(url)

            WebDriverWait(driver, 30).until(
                EC.presence_of_element_located((By.CLASS_NAME, class_name))
            )
            break
        except Exception:
            driver.quit()
            if x == 10:
                raise Exception(
                    "Make sure this ran with a Proxy, will fail without one"
                )
            continue
    return driver


def getVarName(value):
    try:
        return int(value)
    except ValueError:
        pass
    return value


def getJSONObjectVariable(Object, varNames, noVal=MISSING):
    value = noVal
    for varName in varNames.split("."):
        varName = getVarName(varName)
        try:
            value = Object[varName]
            Object = Object[varName]
        except Exception:
            return noVal
    if value is None or value == "":
        return noVal
    return value


def getJSObject(response, varName, noVal=MISSING):
    JSObject = re.findall(f"var {varName} = (.+?);", response)
    if JSObject is None or len(JSObject) == 0:
        return noVal
    return JSObject[0]


def fetchSingleZip(driver, zip):
    log.info(zip)
    try:
        driver.get(f"{website}/locations/atm-listing/")

        inputZip = driver.find_element_by_xpath("//input[contains(@class, 'zipField')]")
        inputZip.send_keys(zip)

        applyButton = driver.find_element_by_xpath("//input[@value='Find Locations']")
        driver.execute_script("arguments[0].click();", applyButton)
    except:
        log.info("CloudFlare Triggered or Page load failed, Retrying...")
        driver.quit()
        urlForDriver = "https://www.lmcu.org/locations/atm-listing/"
        driver = initiateDriver(urlForDriver, "zipField")
        driver.get(f"{website}/locations/atm-listing/")

        inputZip = driver.find_element_by_xpath("//input[contains(@class, 'zipField')]")
        inputZip.send_keys(zip)

        applyButton = driver.find_element_by_xpath("//input[@value='Find Locations']")
        driver.execute_script("arguments[0].click();", applyButton)

    try:
        WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.ID, "map")))
    except:
        pass

    try:
        data = getJSObject(driver.page_source, "jsonlist")
        data = json.loads(data)
        return data["Data"]
    except:
        return []


def fetchData():
    ids = [MISSING]
    urlForDriver = "https://www.lmcu.org/locations/atm-listing/"
    driver = initiateDriver(urlForDriver, "zipField")
    totalZip = 0
    count = 0
    for zipCode in search:
        totalZip = totalZip + 1
        data = fetchSingleZip(driver, zipCode)

        for store in data:
            store_number = getJSONObjectVariable(store, "Id")
            if store_number in ids:
                continue
            ids.append(store_number)
            count = count + 1

            phone = MISSING
            country_code = "US"
            hours_of_operation = MISSING

            page_url = getJSONObjectVariable(store, "LocationUrl")
            if MISSING in page_url:
                page_url = f"{website}/locations/get-locations"

            location_name = getJSONObjectVariable(store, "LocationName")
            if location_name == MISSING:
                location_name = getJSONObjectVariable(store, "BranchName")

            location_type = getJSONObjectVariable(store, "Source")
            street_address = getJSONObjectVariable(store, "Address")
            city = getJSONObjectVariable(store, "City")
            zip_postal = str(getJSONObjectVariable(store, "Zip"))
            if not zip_postal.isdigit():
                country_code = "CA"
            state = getJSONObjectVariable(store, "State")
            latitude = str(getJSONObjectVariable(store, "Latitude"))
            longitude = str(getJSONObjectVariable(store, "Longitude"))

            search.found_location_at(latitude, longitude)

            raw_address = f"{street_address} {city}, {state} {zip_postal}"
            if MISSING in raw_address:
                raw_address = MISSING

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

        if totalZip % 15 == 0:
            driver = initiateDriver(urlForDriver, "zipField", driver=driver)
        log.debug(
            f"{totalZip}. zip {zipCode} => {len(data)} stores; total store = {count}"
        )

    if driver is not None:
        driver.close()
    log.info(f"Total stores = {count}")


def scrape():
    start = time.time()
    result = fetchData()
    with SgWriter() as writer:
        for rec in result:
            writer.write_row(rec)
    end = time.time()
    log.info(f"Scrape took {end - start} seconds.")


if __name__ == "__main__":
    scrape()
