from lxml import html
import time
import json

from sglogging import sglog
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgselenium import SgChrome
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
import ssl

ssl._create_default_https_context = ssl._create_unverified_context


def get_driver(url, class_name, driver=None):
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

            WebDriverWait(driver, 20).until(
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


def driver_sleep(driver, time=2):
    try:
        WebDriverWait(driver, time).until(
            EC.presence_of_element_located((By.ID, MISSING))
        )
    except:
        pass


website = "https://www.bigyellow.co.uk"
MISSING = SgRecord.MISSING
class_name = "d-inline"

log = sglog.SgLogSetup().get_logger(logger_name=website)


def fetch_stores():
    driver = get_driver(f"{website}/find-a-store/", class_name)

    log.debug("Clicking Accept button")
    try:
        driver.find_element_by_xpath("//button[contains(@class, 'dismiss')]").click()
    except Exception as e:
        log.info(f"Oh no!: {e}")
        pass

    body = html.fromstring(driver.page_source, "lxml")
    driver.quit()
    return body.xpath('//ul[contains(@class, "list-stores")]/li/a/@href')


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


def get_hoo(data):
    hoo = []
    for sData in data:
        dayOfWeek = sData["dayOfWeek"]
        opens = sData["opens"]
        closes = sData["closes"]

        if isinstance(dayOfWeek, list):
            for day in dayOfWeek:
                hoo.append(f"{day}: {opens}-{closes}")
        else:
            hoo.append(f"{dayOfWeek}: {opens}-{closes}")
    return "; ".join(hoo)


def fetch_data():
    stores = fetch_stores()
    log.info(f"Total stores = {len(stores)}")
    count = 0

    for store in stores:
        count = count + 1
        page_url = f"{website}{store}"
        log.debug(f"{count}. scrapping {page_url} ...")

        try:
            driver = get_driver(page_url, class_name, driver=None)
        except Exception:
            driver = get_driver(page_url, class_name)

        body = html.fromstring(driver.page_source, "lxml")
        jsons = body.xpath('//script[contains(@type, "application/ld+json")]/text()')
        data = None
        for jsonData in jsons:
            if '"latitude"' in jsonData:
                data = json.loads(jsonData)
                break
        if data is None:
            log.error(f"{count}. {page_url} No json found")
            continue

        store_number = MISSING
        location_type = MISSING

        location_name = get_JSON_object_variable(data, "name")
        street_address = get_JSON_object_variable(data, "address.streetAddress")
        city = get_JSON_object_variable(data, "address.addressLocality")
        zip_postal = get_JSON_object_variable(data, "address.postalCode")
        state = get_JSON_object_variable(data, "address.addressRegion")
        if state == "Bristol" and not city:
            state = ""
            city = "Bristol"
        country_code = get_JSON_object_variable(data, "address.addressCountry")
        phone = get_JSON_object_variable(data, "telephone")
        latitude = get_JSON_object_variable(data, "latitude")
        longitude = get_JSON_object_variable(data, "longitude")
        raw_address = f"{street_address}, {city}, {state} {zip_postal}".replace(
            MISSING, ""
        )
        raw_address = " ".join(raw_address.split())
        raw_address = raw_address.replace(", ,", ",")

        hoo = get_hoo(get_JSON_object_variable(data, "openingHoursSpecification"))

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
            hours_of_operation=hoo,
            raw_address=raw_address,
        )

    driver.quit()
    return []


def scrape():
    log.info(f"Start Crawling {website} ...")
    start = time.time()

    with SgWriter(deduper=SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        for rec in fetch_data():
            writer.write_row(rec)
    end = time.time()
    log.info(f"Scrape took {end-start} seconds.")


if __name__ == "__main__":
    scrape()
