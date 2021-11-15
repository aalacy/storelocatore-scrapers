from sgpostal.sgpostal import parse_address_intl
import time
import json
from lxml import html
from sglogging import sglog
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
import random
from sgselenium.sgselenium import SgChrome
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
import ssl

try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context


website = "unode50.com"
store_url1 = "https://www.unode50.com/us/stores#34.09510173134606,-118.3993182825743"
store_url = "view-source:https://www.unode50.com/us/stores"
MISSING = SgRecord.MISSING
log = sglog.SgLogSetup().get_logger(logger_name=website)


def driver_sleep(driver, time=2):
    try:
        WebDriverWait(driver, time).until(
            EC.presence_of_element_located((By.ID, MISSING))
        )
    except Exception:
        pass


def random_sleep(driver, start=5, limit=3):
    driver_sleep(driver, random.randint(start, start + limit))


def fetch_stores():
    with SgChrome(
        executable_path=ChromeDriverManager().install(), is_headless=True
    ) as driver:

        driver.maximize_window()
        random_sleep(driver, 1)

        driver.get("https://www.unode50.com")
        random_sleep(driver, 10)

        try:
            lButton = driver.find_element_by_xpath(
                "//button[contains(@id, 'btn-cookie-allow')]"
            )
            driver.execute_script("arguments[0].click();", lButton)
            random_sleep(driver, 10)
        except Exception as e:
            log.info(e)
            pass

        tried = 0
        while True:
            tried = tried + 1

            if tried == 10:
                break

            log.debug(f"Trying {tried} ...")
            try:
                driver.get(store_url1)
                driver.forward()
                driver.get(store_url)
                driver.forward()
                random_sleep(driver, 12)

                body = html.fromstring(driver.page_source, "lxml")

                data = body.xpath(
                    "//td[contains(text(), 'store-locator-search') and contains(text(), 'Magento_Ui/js/core/app')]/text()"
                )[0]
                data = json.loads(data)
                return data["*"]["Magento_Ui/js/core/app"]["components"][
                    "store-locator-search"
                ]["markers"]
            except Exception as e:
                log.info(f"Failed Locading redirected page: {e}")
                pass
    return []


def get_address(raw_address):
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
        log.info(f"Missing address: {e}")
        pass
    return MISSING, MISSING, MISSING, MISSING


def fetch_data():
    stores = fetch_stores()
    log.info(f"Total stores = {len(stores)}")
    for store in stores:
        country_code = MISSING
        phone = MISSING
        location_type = MISSING
        hours_of_operation = MISSING

        store_number = store["id"]
        location_name = store["name"]
        raw_address = store["address"].replace("\n", ", ").replace("\t", ", ")
        raw_address = " ".join(raw_address.split())
        raw_address = raw_address.replace(", ,", ",").replace(",,", ",")
        if raw_address[len(raw_address) - 1] == ",":
            raw_address = raw_address[:-1]

        street_address, city, state, zip_postal = get_address(raw_address)
        latitude = store["latitude"]
        longitude = store["longitude"]
        page_url = f"https://www.unode50.com/en/int/stores#{latitude},{longitude}"

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
    with SgWriter(
        deduper=SgRecordDeduper(RecommendedRecordIds.StoreNumberId)
    ) as writer:
        for rec in fetch_data():
            writer.write_row(rec)
    end = time.time()
    log.info(f"Scrape took {end-start} seconds.")


if __name__ == "__main__":
    scrape()
