import time
import json
import re

from sglogging import sglog
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgzip.dynamic import DynamicZipSearch, SearchableCountries, Grain_2
from sgscrape.pause_resume import CrawlStateSingleton

from sgselenium.sgselenium import SgChrome
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

import ssl

ssl._create_default_https_context = ssl._create_unverified_context

DOMAIN = "lmcu.org"
website = "https://www.lmcu.org"

MISSING = SgRecord.MISSING

log = sglog.SgLogSetup().get_logger(logger_name=DOMAIN)


def initiate_driver(url, class_name, driver=None):
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


def get_var_name(value):
    try:
        return int(value)
    except ValueError:
        pass
    return value


def get_json_object_variable(Object, varNames, noVal=MISSING):
    value = noVal
    for varName in varNames.split("."):
        varName = get_var_name(varName)
        try:
            value = Object[varName]
            Object = Object[varName]
        except Exception:
            return noVal
    if value is None or value == "":
        return noVal
    return value


def get_js_object(response, varName, noVal=MISSING):
    JSObject = re.findall(f"var {varName} = (.+?);", response)
    if JSObject is None or len(JSObject) == 0:
        return noVal
    return JSObject[0]


def fetch_single_zip(driver, zip):
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
        driver = initiate_driver(urlForDriver, "zipField")
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
        data = get_js_object(driver.page_source, "jsonlist")
        data = json.loads(data)
        return data["Data"]
    except:
        return []


def fetch_data(search):
    ids = [MISSING]
    urlForDriver = "https://www.lmcu.org/locations/atm-listing/"
    driver = initiate_driver(urlForDriver, "zipField")
    totalZip = 0
    count = 0
    states = CrawlStateSingleton.get_instance()
    for zipCode in search:
        totalZip = totalZip + 1
        data = fetch_single_zip(driver, zipCode)

        for store in data:
            store_number = get_json_object_variable(store, "Id")
            if store_number in ids:
                continue
            ids.append(store_number)
            count = count + 1

            phone = MISSING
            country_code = "US"
            hours_of_operation = MISSING

            page_url = get_json_object_variable(store, "LocationUrl")
            if MISSING in page_url:
                page_url = f"{website}/locations/get-locations"

            location_name = get_json_object_variable(store, "LocationName")
            if location_name == MISSING:
                location_name = get_json_object_variable(store, "BranchName")

            location_type = get_json_object_variable(store, "Source")
            street_address = get_json_object_variable(store, "Address")
            city = get_json_object_variable(store, "City")
            zip_postal = str(get_json_object_variable(store, "Zip"))
            if not zip_postal.isdigit():
                country_code = "CA"
            state = get_json_object_variable(store, "State")
            latitude = str(get_json_object_variable(store, "Latitude"))
            longitude = str(get_json_object_variable(store, "Longitude"))

            search.found_location_at(latitude, longitude)

            raw_address = f"{street_address} {city}, {state} {zip_postal}"
            if MISSING in raw_address:
                raw_address = MISSING

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

            try:
                rec_count = states.get_misc_value(
                    search.current_country(), default_factory=lambda: 0
                )
                states.set_misc_value(search.current_country(), rec_count + 1)
            except Exception as e:
                log.error(f"MISE {zipCode}, message={e}")

        if totalZip % 15 == 0:
            driver = initiate_driver(urlForDriver, "zipField", driver=driver)
        log.debug(
            f"{totalZip}. zip {zipCode} => {len(data)} stores; total store = {count}"
        )

    if driver is not None:
        driver.close()
    log.info(f"Total stores = {count}")


def scrape():
    start = time.time()
    search = DynamicZipSearch(
        country_codes=[SearchableCountries.USA],
        max_search_distance_miles=None,
        max_search_results=None,
        granularity=Grain_2(),
    )
    with SgWriter(
        deduper=SgRecordDeduper(RecommendedRecordIds.StoreNumberId)
    ) as writer:
        for rec in fetch_data(search):
            writer.write_row(rec)

    state = CrawlStateSingleton.get_instance()
    log.debug("Printing number of records by country-code:")
    for country_code in SearchableCountries.USA:
        try:
            count = state.get_misc_value(country_code, default_factory=lambda: 0)
            log.debug(f"{country_code}: {count}")
        except Exception as e:
            log.info(f"Country codes: {country_code}, message={e}")
            pass

    end = time.time()
    log.info(f"Scrape took {end - start} seconds.")


if __name__ == "__main__":
    scrape()
