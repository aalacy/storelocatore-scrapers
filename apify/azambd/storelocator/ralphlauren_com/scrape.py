from lxml import html
import time
import json
import random

from sglogging import sglog
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord

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
    # Handle target environment that doesn't support HTTPS verification
    ssl._create_default_https_context = _create_unverified_https_context

DOMAIN = "ralphlauren.com"
website = "https://www.ralphlauren.com"
MISSING = "<MISSING>"

log = sglog.SgLogSetup().get_logger(logger_name=DOMAIN)

countryCodes = ["CA", "GB", "US"]


def driverSleep(driver, time=2):
    try:
        WebDriverWait(driver, time).until(
            EC.presence_of_element_located((By.ID, MISSING))
        )
    except Exception:
        pass


def randomSleep(driver, start=5, limit=6):
    driverSleep(driver, random.randint(start, start + limit))


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
    if value is None or value == "None" or value == "":
        return MISSING
    return value


def fetchStores():
    user_agent = (
        "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:78.0) Gecko/20100101 Firefox/78.0"
    )
    x = 0
    driver = None
    while True:
        x = x + 1
        try:
            driver = SgChrome(
                executable_path=ChromeDriverManager().install(),
                user_agent=user_agent,
                is_headless=True,
            ).driver()

            log.debug("Loading store page ...")
            driver.get(f"{website}/stores")
            randomSleep(driver, 10)
            body = html.fromstring(driver.page_source, "lxml")
            allCountryCodes = body.xpath(
                "//select[@id='dwfrm_storelocator_country']/option/@value"
            )

            allStores = []
            for countryCode in countryCodes:
                if countryCode not in allCountryCodes:
                    log.debug(f"{countryCode} not in store options")
                log.debug(f"Fetching country {countryCode} ...")
                driver.get(
                    f"{website}/findstores?dwfrm_storelocator_country={countryCode}&dwfrm_storelocator_findbycountry=Search&findByValue=CountrySearch"
                )
                randomSleep(driver, 20)
                body = html.fromstring(driver.page_source, "lxml")

                stores = json.loads(
                    body.xpath(
                        '//div[contains(@class, "storeJSON hide")]/@data-storejson'
                    )[0]
                )
                jsonData = body.xpath(
                    '//script[contains(@type, "application/ld+json")]/text()'
                )

                for data in jsonData:
                    if 'store":[{' in data:
                        dataJSON = json.loads(data)["store"]
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

                allStores = allStores + stores
            return driver, allStores

        except Exception as e:
            log.error(f"Error loading : {e}")
            driver.quit()
            if x == 3:
                raise Exception(
                    "Make sure this ran with a Proxy, will fail without one"
                )
            continue
    return driver, []


def fetchData():
    driver, stores = fetchStores()
    log.info(f"Total stores = {len(stores)}")
    for store in stores:

        location_type = MISSING

        store_number = getJSONObjectVariable(store, "id")
        page_url = f"{website}/Stores-Details?StoreID={store_number}"
        location_name = getJSONObjectVariable(store, "location_name")
        street_address = getJSONObjectVariable(store, "street_address")
        city = getJSONObjectVariable(store, "city")
        state = getJSONObjectVariable(store, "stateCode")
        zip_postal = getJSONObjectVariable(store, "postalCode")
        country_code = getJSONObjectVariable(store, "country_code")
        phone = getJSONObjectVariable(store, "phone")
        latitude = getJSONObjectVariable(store, "latitude")
        longitude = getJSONObjectVariable(store, "longitude")

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
                    dataJSON = json.loads(data)
                    location_name = dataJSON["name"]
                    hours_of_operation = (
                        "; ".join(dataJSON["openingHours"])
                        .replace("<br/>\n", "; ")
                        .replace("<br/>", " ")
                        .replace("<br>", "; ")
                        .replace("\n", " ")
                        .strip()
                    )
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
    driver.quit()
    return []


def scrape():
    log.info(f"Scrape started ...")
    start = time.time()
    result = fetchData()
    with SgWriter() as writer:
        for rec in result:
            writer.write_row(rec)
    end = time.time()
    log.info(f"Scrape took {end-start} seconds.")


if __name__ == "__main__":
    scrape()
