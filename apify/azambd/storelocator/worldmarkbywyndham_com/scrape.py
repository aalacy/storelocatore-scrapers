from sgpostal.sgpostal import parse_address_intl
from lxml import html
import time
import json
import re

from sglogging import sglog
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds

from sgselenium.sgselenium import SgChrome
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By

from sgscrape.pause_resume import CrawlStateSingleton

import ssl

ssl._create_default_https_context = ssl._create_unverified_context

DOMAIN = "wyndhamdestinations.com"
website = "https://worldmark.wyndhamdestinations.com"
MISSING = "<MISSING>"
resorts_page = f"{website}/us/en/resorts/resort-search-results"

user_agent = (
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:78.0) Gecko/20100101 Firefox/78.0"
)

log = sglog.SgLogSetup().get_logger(logger_name=DOMAIN)


def initiateDriver(driver=None):
    if driver is not None:
        driver.quit()

    return SgChrome(
        is_headless=True,
        user_agent=user_agent,
    ).driver()


def driverSleep(driver, time=5):
    try:
        WebDriverWait(driver, time).until(
            EC.presence_of_element_located((By.ID, MISSING))
        )
    except Exception:
        pass


def fetchStores():
    log.info("Start with drive initiation")
    driver = initiateDriver()

    x = 0
    while True:
        x = x + 1
        try:
            driver.get(resorts_page)
            delay = 1

            while delay < 60:
                driverSleep(driver)
                if 'class="resort-cardV2__name"' in driver.page_source:
                    break
                delay = delay + 1

            screen_height = driver.execute_script("return document.body.scrollHeight;")

            pages = 1
            while True:
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                pages = pages + 1

                delay = 1
                while delay < 60:
                    driverSleep(driver)
                    new_screen_height = driver.execute_script(
                        "return document.body.scrollHeight;"
                    )
                    if screen_height != new_screen_height:
                        log.info(f"scrapping page={pages}")
                        driver.execute_script(
                            "window.scrollTo(0, document.body.scrollHeight);"
                        )
                        break
                    delay = delay + 1

                new_screen_height = driver.execute_script(
                    "return document.body.scrollHeight;"
                )

                if screen_height == new_screen_height:
                    break
                screen_height = new_screen_height

            body = html.fromstring(driver.page_source, "lxml")
            resort_divs = body.xpath(
                '//div[contains(@class, "resort-cardV2__content")]'
            )
            log.info(f"Total resorts divs = {len(resort_divs)}")
            stores = []
            for resort_div in resort_divs:
                title = resort_div.xpath('.//div[@class="resort-cardV2__name"]/a')[0]
                page_url = title.xpath(".//@href")[0]
                location_name = title.xpath(".//text()")[0]
                stores.append(
                    {
                        "location_name": location_name,
                        "page_url": website + page_url,
                    }
                )
            return driver, stores
            break
        except Exception as e:
            log.error(f"Failed to initiate {e}")
            if x == 3:
                driver.quit()
                raise Exception(
                    "Make sure this ran with a Proxy, will fail without one"
                )
                break
            continue
    return driver, []


def fetchSingleStore(driver, page_url):
    driver.get(page_url)
    delay = 0
    driverSleep(driver)
    while delay < 30:
        if "Sorry!" in driver.page_source:
            return None
        if '"latitude"' in driver.page_source:
            return driver.page_source
        driverSleep(driver)
        delay = delay + 1
    return None


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
    return value


def getReviewedPath(jsonData, path):
    for data in jsonData:
        value = getJSONObjectVariable(data, path)
        if path != MISSING:
            return value

    return MISSING


def getJSObject(response, varName, noVal=MISSING):
    JSObject = re.findall(f'"{varName}":"(.+?)"', response)
    if JSObject is None or len(JSObject) == 0:
        return noVal
    data = JSObject[0].replace('"', "").replace(",", "").strip()
    if len(data) == 0:
        return noVal
    return data


def getAddress(raw_address):
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
        log.info(f"Address is missing {e}")
        pass
    return MISSING, MISSING, MISSING, MISSING


def fetchData():
    driver, stores = fetchStores()
    log.info(f"Total stores = {len(stores)}")

    noStore = 0
    error = 0
    for store in stores:
        noStore = noStore + 1

        page_url = store["page_url"]
        location_name = store["location_name"]

        log.info(f"{noStore}. Scrapping {page_url} ...")
        response = fetchSingleStore(driver, page_url)
        if response is None:
            error = error + 1
            log.error(f"ERROR #{error}. can't load: {location_name} , {page_url}")
            continue
        body = html.fromstring(response, "lxml")
        data = body.xpath('//script[contains(@type, "application/ld+json")]/text()')
        jsonData = None
        for sData in data:
            if "latitude" in sData:
                jsonData = json.loads(sData)

        store_number = MISSING
        location_type = MISSING
        street_address = getReviewedPath(jsonData, "itemReviewed.address.streetAddress")
        zip_postal = getReviewedPath(jsonData, "itemReviewed.address.postalCode")
        state = getReviewedPath(jsonData, "itemReviewed.address.addressRegion")
        raw_address = None

        phone = getReviewedPath(jsonData, "itemReviewed.telephone.0")
        latitude = getReviewedPath(jsonData, "itemReviewed.geo.latitude")
        longitude = getReviewedPath(jsonData, "itemReviewed.geo.longitude")
        log.info(f"{latitude}, {longitude}")
        hours_of_operation = MISSING
        city = getJSObject(response, "addressLocality")

        resort_address = (
            (", ")
            .join(body.xpath('//div[contains(@class, "resort-address")]/text()'))
            .replace(" ,", ",")
            .replace("  ", " ")
            .strip()
        )

        if len(resort_address) > 0:
            if len(resort_address) > 0:
                street_address1, city1, state1, zip_postal1 = getAddress(resort_address)

                if (
                    street_address1 != MISSING
                    and city1 != MISSING
                    and state1 != MISSING
                    and zip_postal1 != MISSING
                ):
                    raw_address = resort_address
                    street_address = street_address1
                    city = city1
                    state = state1
                    zip_postal = zip_postal1

                if (
                    street_address1 != MISSING
                    and city1 != MISSING
                    and zip_postal1 != MISSING
                ):
                    street_address = street_address1
                    city = city1
                    zip_postal = zip_postal1

                if (
                    street_address1 != MISSING
                    and city1 != MISSING
                    and state1 != MISSING
                ):
                    street_address = street_address1
                    city = city1
                    state = state1

                if street_address1 != MISSING and city1 != MISSING:
                    street_address = street_address1
                    city = city1

                else:
                    if city == MISSING and city1 != MISSING:
                        city = city1
                    if street_address == MISSING and street_address1 != MISSING:
                        street_address = street_address1
                    if city == MISSING:
                        resort_address = resort_address.split(", ")
                        if len(resort_address) > 2:
                            city = resort_address[len(resort_address) - 2]

        if city == MISSING:
            raw_address = f"{street_address}, {state} {zip_postal}"
        elif raw_address is None:
            raw_address = f"{street_address}, {city}, {state} {zip_postal}"

        if MISSING in raw_address:
            raw_address = MISSING

        if "mexico" in page_url:
            country_code = "MX"
        elif "canada" in page_url:
            country_code = "CA"
        elif "fiji" in page_url:
            country_code = "FJ"
        else:
            country_code = "US"

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
    log.info(f"Total error page ={error}")
    driver.quit()
    return []


def scrape():
    CrawlStateSingleton.get_instance().save(override=True)
    start = time.time()
    with SgWriter(deduper=SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        for rec in fetchData():
            writer.write_row(rec)
    end = time.time()
    log.info(f"Scrape took {end-start} seconds.")


if __name__ == "__main__":
    scrape()
