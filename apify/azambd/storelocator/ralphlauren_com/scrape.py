from lxml import html
import time
import random
import json
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
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import NoSuchElementException
import ssl

ssl._create_default_https_context = ssl._create_unverified_context

website = "ralphlauren.com"
start_url = "https://www.ralphlauren.com/findstores?dwfrm_storelocator_distanceUnit=mi&dwfrm_storelocator_searchKey=10002&dwfrm_storelocator_maxdistance=50000&dwfrm_storelocator_latitude=&dwfrm_storelocator_longitude=&countryCode=&postalCode=&usePlaceDetailsAddress=false&dwfrm_storelocator_findbysearchkey=Search&findByValue=KeySearch"
user_agent = (
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:78.0) Gecko/20100101 Firefox/78.0"
)
MISSING = SgRecord.MISSING

xpath_px_captcha = '//*[@id="px-captcha"]'
EXPLICIT_WAIT_TIME = 10


def driver_sleep(driver, time=2):
    try:
        WebDriverWait(driver, time).until(
            EC.presence_of_element_located((By.ID, MISSING))
        )
    except Exception:
        pass


def random_sleep(driver, start=5, limit=3):
    driver_sleep(driver, random.randint(start, start + limit))


def check_if_xpath_exists(driver, xpath):
    try:
        driver.find_element_by_xpath(xpath)
    except NoSuchElementException:
        return False
    return True


log = sglog.SgLogSetup().get_logger(logger_name=website)


def fetch_page_cf(driver, url):
    driver.get(url)
    random_sleep(driver, 5)
    driver.execute_script("window.scrollTo(0, document.documentElement.scrollHeight);")
    driver.execute_script("window.scrollTo(0, 0);")
    driver.execute_script("window.scrollTo(0, document.documentElement.scrollHeight);")
    random_sleep(driver, 2)

    if check_if_xpath_exists(driver, xpath_px_captcha) is True:
        try:
            log.info("Dealing with CF ...")
            WebDriverWait(driver, EXPLICIT_WAIT_TIME).until(
                EC.presence_of_element_located((By.ID, "px-captcha"))
            )
            block_button_px = driver.find_element_by_id("px-captcha")
            action = ActionChains(driver)
            x = 50
            y = 50
            action.move_to_element_with_offset(block_button_px, x, y)
            log.debug(f"Moving the cursor closer to the PRESS & HOLD button {x}, {y}")
            random_sleep(driver, 10)
            action.click_and_hold()
            log.debug("Perform click and hold")
            action.perform()
            log.debug("Holding for a few seconds")
            random_sleep(driver, 8)
            log.debug("Pressed button")
            action.release().perform()
            log.debug("PRESS & HOLD BUTTON RELEASED")

            random_sleep(driver, 30)

            driver.execute_script("window.scrollTo(0, 0);")
            random_sleep(driver, 10)
            log.debug(f"Reloading again {url} ...")
            return fetch_page_cf(driver, url)
        except Exception as e:
            log.debug(f"Retrying ...{e}")
            return fetch_page_cf(driver, url)
    else:
        random_sleep(driver, 5)


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
    value = str(value).replace("null", "").replace("None", "").strip()
    if len(value) == 0:
        return MISSING
    return value


def fetch_stores(driver):
    fetch_page_cf(driver, start_url)
    body = html.fromstring(driver.page_source, "lxml")
    data = body.xpath('//*[contains(@data-storejson, "[")]/@data-storejson')[0]
    stores = json.loads(data)
    jsons = body.xpath('//script[contains(@type, "application/ld+json")]/text()')
    dataJSON = []
    for jsonData in jsons:
        if '"openingHours"' in jsonData:
            dataJSON = json.loads(jsonData)
            dataJSON = dataJSON["store"]
            break

    for store in stores:
        store["location_name"] = MISSING
        store["street_address"] = MISSING
        store["hoo"] = MISSING
        store["country_code"] = "US"

        if "latitude" not in store:
            continue
        for data in dataJSON:
            if data["telephone"] == "":
                data_phone = "None"
            else:
                data_phone = data["telephone"]
            if (
                "latitude" in data["geo"]
                and f"{data_phone}" == f'{store["phone"]}'
                and f'{data["geo"]["latitude"]} {data["geo"]["longitude"]}'
                == f'{store["latitude"]} {store["longitude"]}'
            ):
                store["location_name"] = data["name"]
                store["street_address"] = data["address"]["streetAddress"]
                store["country_code"] = data["address"]["addressCountry"]
                store["hoo"] = (
                    data["openingHours"]
                    .replace("<br/>\n", "; ")
                    .replace("<br/>", " ")
                    .replace("<br>", "; ")
                    .replace("\n", " ")
                    .strip()
                )

    return stores


def fetch_data(driver):
    stores = fetch_stores(driver)
    log.info(f"Total stores = {len(stores)}")
    for store in stores:
        location_type = MISSING

        store_number = get_JSON_object_variable(store, "id")
        page_url = f"https://www.ralphlauren.com/Stores-Details?StoreID={store_number}"
        location_name = get_JSON_object_variable(store, "location_name")
        location_name = location_name.split("-")[0].strip()
        street_address = get_JSON_object_variable(store, "street_address")
        city = get_JSON_object_variable(store, "city")
        zip_postal = get_JSON_object_variable(store, "postalCode")
        street_address = street_address.replace(f",{zip_postal}", "")
        state = get_JSON_object_variable(store, "stateCode")
        country_code = get_JSON_object_variable(store, "countryCode")
        phone = get_JSON_object_variable(store, "phone")
        latitude = get_JSON_object_variable(store, "latitude")
        longitude = get_JSON_object_variable(store, "longitude")

        hours_of_operation = get_JSON_object_variable(store, "hoo")

        raw_address = f"{street_address}, {city}, {state} {zip_postal}".replace(
            MISSING, ""
        )
        raw_address = " ".join(raw_address.split())
        raw_address = raw_address.replace(", ,", ",").replace(",,", ",")
        if raw_address[len(raw_address) - 1] == ",":
            raw_address = raw_address[:-1]

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
    count = 0
    with SgChrome(
        executable_path=ChromeDriverManager().install(),
        is_headless=True,
        user_agent=user_agent,
    ) as driver:
        with SgWriter(
            deduper=SgRecordDeduper(RecommendedRecordIds.PageUrlId)
        ) as writer:
            for rec in fetch_data(driver):
                writer.write_row(rec)
                count = count + 1
    end = time.time()
    log.info(f"Total Rows Added= {count}")
    log.info(f"Scrape took {end-start} seconds.")


if __name__ == "__main__":
    scrape()
