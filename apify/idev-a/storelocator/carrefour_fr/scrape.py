from lxml import html
import random
import os
import ssl
import time
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from sgselenium.sgselenium import SgChrome
from sglogging import sglog
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds

os.environ[
    "PROXY_URL"
] = "http://groups-RESIDENTIAL,country-us:{}@proxy.apify.com:8000/"
ssl._create_default_https_context = ssl._create_unverified_context


website = "https://www.carrefour.fr"
store_url = f"{website}/magasin/"
MISSING = SgRecord.MISSING

log = sglog.SgLogSetup().get_logger(logger_name=website)

chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("start-maximized")
chrome_options.add_argument("--disable-notifications")
chrome_options.add_argument("--mute-audio")
chrome_options.add_argument(
    "user-agent=Mozilla/5.0 (iPhone; CPU iPhone OS 10_3 like Mac OS X) AppleWebKit/602.1.50 (KHTML, like Gecko) CriOS/56.0.2924.75 Mobile/14E5239e Safari/602.1"
)


def request_with_retries(driver, url):
    driver.get(url)
    random_sleep(driver)


def driver_sleep(driver, time=2):
    try:
        WebDriverWait(driver, time).until(
            EC.presence_of_element_located((By.ID, MISSING))
        )
    except Exception:
        pass


def random_sleep(driver, start=5, limit=3):
    driver_sleep(driver, random.randint(start, start + limit))


def fetch_regions(driver):
    request_with_retries(driver, store_url)
    driver_sleep(driver, 30)
    body = html.fromstring(driver.page_source, "lxml")
    return body.xpath(
        '//li[contains(@class, "store-locator-footer-list__item")]/a/@href'
    )


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
    if value is None:
        return MISSING
    value = f"{value}"
    if len(value) == 0:
        return MISSING
    return value


def get_hoo(timeRange={}):
    try:
        keys = timeRange.keys()
        if len(keys) == 0:
            return MISSING
        hoo = []
        for key in keys:
            val = timeRange[key]
            begTime = val["begTime"]["date"].split()[1].split(":00.00")[0]
            endTime = val["endTime"]["date"].split()[1].split(":00.00")[0]
            hoo.append(f"{key}: {begTime}-{endTime}")
        return "; ".join(hoo)
    except Exception:
        return MISSING


def fetch_data(driver):
    regions = fetch_regions(driver)
    log.info(f"Total regions = {len(regions)}")
    count = 0

    for region in regions:
        count = count + 1
        url = website + region
        log.info(f"{count}: scrapping {url} ...")
        request_with_retries(driver, url)
        data = (
            driver.page_source.split("window.ONECF_INITIAL_STATE =")[1]
            .split("window.ONECF")[0]
            .replace("&quot;", '"')
            .strip()[0:-1]
        )

        stores = json.loads(data)["search"]["data"]["stores"]
        log.debug(f"stores found {len(stores)}")

        for store in stores:
            store_number = store["id"]
            page_url = f"{website}{store['storePageUrl']}"
            location_name = store["name"]
            location_type = get_JSON_object_variable(store, "format")

            address = store["address"]
            geo = address["geoCoordinates"]
            street_address = (
                get_JSON_object_variable(address, "address1")
                + " "
                + get_JSON_object_variable(address, "address2")
                + " "
                + get_JSON_object_variable(address, "address3")
            )
            street_address = street_address.replace(MISSING, "").strip()
            city = get_JSON_object_variable(address, "city")
            zip_postal = get_JSON_object_variable(address, "postalCode")
            state = get_JSON_object_variable(address, "region")
            country_code = "FR"
            phone = get_JSON_object_variable(store, "phoneNumber")
            latitude = get_JSON_object_variable(geo, "latitude")
            longitude = get_JSON_object_variable(geo, "longitude")
            hours_of_operation = get_hoo(store["openingWeekPattern"]["timeRanges"])
            raw_address = f"{street_address}, {city}, {state} {zip_postal}".replace(
                MISSING, ""
            )
            raw_address = " ".join(raw_address.split())
            raw_address = raw_address.replace(", ,", ",").replace(",,", ",")
            if raw_address[len(raw_address) - 1] == ",":
                raw_address = raw_address[:-1]

            if page_url == store_url:
                continue

            if latitude == MISSING or longitude == MISSING:
                log.info(f"{page_url, location_type, store}")
                location_type = "Fermé temporairement"
            yield SgRecord(
                locator_domain="carrefour.fr",
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
    with SgChrome(chrome_options=chrome_options) as driver:
        with SgWriter(
            deduper=SgRecordDeduper(RecommendedRecordIds.PageUrlId)
        ) as writer:
            for rec in fetch_data(driver):
                writer.write_row(rec)
    end = time.time()
    log.info(f"Scrape took {end-start} seconds.")


if __name__ == "__main__":
    scrape()
