from lxml import html
import time
import json
import random

from sglogging import sglog
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds

from sgselenium.sgselenium import SgChrome
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By

import ssl

ssl._create_default_https_context = ssl._create_unverified_context

DOMAIN = "ralphlauren.com"
website = "https://www.ralphlauren.com"
MISSING = "<MISSING>"

log = sglog.SgLogSetup().get_logger(logger_name=DOMAIN)


def driver_sleep(driver, time=2):
    try:
        WebDriverWait(driver, time).until(
            EC.presence_of_element_located((By.ID, MISSING))
        )
    except Exception:
        pass


def random_sleep(driver, start=5, limit=3):
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
    if value is None or value == "None" or value == "":
        return MISSING
    return value


def click_close(driver):
    for closeButton in driver.find_elements_by_xpath("//button[@title='Close']"):
        try:
            closeButton.click()
            random_sleep(driver, 3)
        except Exception:
            pass

    driver.maximize_window()


def fetch_country(driver, countryCode):
    random_sleep(driver, 10)
    try:
        driver.implicitly_wait(10)
        driver.find_element_by_xpath(f"//option[@value='{countryCode}']").click()
        element = driver.find_element_by_css_selector("button.search")
        driver.execute_script("arguments[0].click();", element)
        driver.implicitly_wait(30)
    except Exception as e:
        log.info(f"Page does not contain any content for {countryCode} country, {e}")
        pass


def fetch_stores():
    x = 0
    driver = None
    while True:
        x = x + 1
        try:
            driver = SgChrome(
                executable_path=ChromeDriverManager().install(),
                is_headless=False,
            ).driver()

            log.debug("Loading store page ...")
            driver.get(f"{website}/stores")
            random_sleep(driver, 20)
            body = html.fromstring(driver.page_source, "lxml")
            allCountryCodes = body.xpath(
                "//select[@id='dwfrm_storelocator_country']/option/@value"
            )
            click_close(driver)
            allStores = []
            countCountry = 0
            log.debug(f"Total countries = {len(allCountryCodes)}")

            for countryCode in allCountryCodes:
                if len(countryCode) == 0:
                    continue
                countCountry = countCountry + 1
                url = f"{website}/findstores?dwfrm_storelocator_country={countryCode}&dwfrm_storelocator_findbycountry=Search&findByValue=CountrySearch"
                log.debug(
                    f"{countCountry}. Fetching country {countryCode} url = {url}..."
                )
                fetch_country(driver, countryCode)

                body = html.fromstring(driver.page_source, "lxml")
                try:
                    stores = body.xpath(
                        '//*[contains(@data-storejson, "[")]/@data-storejson'
                    )
                    stores = json.loads(stores[0])
                except Exception:
                    log.error("Failed to load store list")
                    stores = []

                log.debug(f"Total stores = {len(stores)}")

                jsonData = body.xpath(
                    '//script[contains(@type, "application/ld+json")]/text()'
                )
                log.debug(f"Total jsonData = {len(jsonData)}")

                for data in jsonData:
                    if 'store":[{' in data:
                        try:
                            dataJSON = json.loads(data)["store"]
                        except Exception:
                            log.error("Failed to load dataJSON ")
                            dataJSON = []

                        log.info(f"total stores in {countryCode} are {len(stores)}")
                        for store in stores:
                            store["location_name"] = MISSING
                            store["street_address"] = MISSING
                            store["hoo"] = MISSING
                            store["country_code"] = "US"
                            if "latitude" not in store:
                                continue

                            for data in dataJSON:
                                if (
                                    "latitude" in data["geo"]
                                    and f'{data["geo"]["latitude"]} {data["geo"]["longitude"]}'
                                    == f'{store["latitude"]} {store["longitude"]}'
                                ):
                                    store["location_name"] = data["name"]
                                    store["street_address"] = data["address"][
                                        "streetAddress"
                                    ]
                                    store["country_code"] = data["address"][
                                        "addressCountry"
                                    ]
                                    store["hoo"] = (
                                        data["openingHours"]
                                        .replace("<br/>\n", "; ")
                                        .replace("<br/>", " ")
                                        .replace("<br>", "; ")
                                        .replace("\n", " ")
                                        .strip()
                                    )
                log.debug(
                    f"{countCountry}. from {countryCode} total store = {len(stores)}..."
                )
                allStores = allStores + stores
                driver.get(f"{website}/stores")

            return driver, allStores

        except Exception as e:
            log.error(f"Error loading : {e}")
            driver.quit()
            if x == 2:
                raise Exception(
                    "Make sure this ran with a Proxy, will fail without one"
                )
            continue
    return driver, []


def fetch_data():
    driver, stores = fetch_stores()
    log.info(f"Total stores = {len(stores)}")
    for store in stores:

        location_type = MISSING

        store_number = get_JSON_object_variable(store, "id")
        page_url = f"{website}/Stores-Details?StoreID={store_number}"
        location_name = get_JSON_object_variable(store, "location_name")
        location_name = location_name.split("-")[0].strip()
        street_address = get_JSON_object_variable(store, "street_address")
        city = get_JSON_object_variable(store, "city")
        state = get_JSON_object_variable(store, "stateCode")
        zip_postal = get_JSON_object_variable(store, "postalCode")
        country_code = get_JSON_object_variable(store, "country_code")
        phone = get_JSON_object_variable(store, "phone")
        latitude = get_JSON_object_variable(store, "latitude")
        longitude = get_JSON_object_variable(store, "longitude")

        street_address = street_address.replace(f",{zip_postal}", "").replace(",", ", ")
        street_address = " ".join(street_address.split())
        if state == MISSING:
            raw_address = f"{street_address}, {city} {zip_postal}"
        else:
            raw_address = f"{street_address}, {city}, {state} {zip_postal}"

        hours_of_operation = store["hoo"]

        if location_name == MISSING:
            log.debug(f"Fetching page_url {page_url} ...")
            driver.get(page_url)
            body = html.fromstring(driver.page_source, "lxml")
            jsonData = body.xpath(
                '//script[contains(@type, "application/ld+json")]/text()'
            )

            for data in jsonData:
                if '"openingHours"' in data:
                    try:
                        dataJSON = json.loads(data)
                    except Exception as e:
                        log.error(f"Failed to load json openingHours: {e}")
                        dataJSON = []
                    location_name = dataJSON["name"]
                    hours_of_operation = (
                        "; ".join(dataJSON["openingHours"])
                        .replace("<br/>\n", "; ")
                        .replace("<br/>", " ")
                        .replace("<br>", "; ")
                        .replace("\n", " ")
                        .strip()
                    )

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
        )
    driver.quit()
    return []


def scrape():
    log.info("Crawling started ...")
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
