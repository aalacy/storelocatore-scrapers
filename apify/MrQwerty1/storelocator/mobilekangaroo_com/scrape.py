from sgpostal.sgpostal import parse_address_intl
import re
from lxml import html
import random
import ssl
import time
from sgselenium.sgselenium import SgChrome
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from sglogging import sglog
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds

ssl._create_default_https_context = ssl._create_unverified_context


def driver_sleep(driver, time=2):
    try:
        WebDriverWait(driver, time).until(
            EC.presence_of_element_located((By.ID, MISSING))
        )
    except Exception:
        pass


def random_sleep(driver, start=5, limit=3):
    driver_sleep(driver, random.randint(start, start + limit))


website = "https://mobilekangaroo.com"
page_url = f"{website}/locations"
MISSING = SgRecord.MISSING

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

log = sglog.SgLogSetup().get_logger(logger_name=website)


def get_phone(Source):
    phone = MISSING

    if Source is None or Source == "":
        return phone

    for match in re.findall(r"[\+\(]?[1-9][0-9 .\-\(\)]{8,}[0-9]", Source):
        phone = match
        return phone
    return phone


def fetch_stores():
    with SgChrome(
        executable_path=ChromeDriverManager().install(), is_headless=True
    ) as driver:
        driver.get(page_url)
        random_sleep(driver)
        mainColumns = driver.find_elements_by_xpath(
            './/div[contains(@class, "bubble-element RepeatingGroup")]'
        )

        itemXpath = (
            './/div[contains(@class, "bubble-element GroupItem group-item entry-")]'
        )
        for mainColumn in mainColumns:
            rows = mainColumn.find_elements_by_xpath(itemXpath)
            sameCount = 0
            lastCount = len(rows)
            if lastCount < 5:
                continue
            while True:
                sameCount = sameCount + 1
                driver.execute_script(
                    "return arguments[0].scrollIntoView(true);", rows[len(rows) - 1]
                )
                rows = mainColumn.find_elements_by_xpath(itemXpath)

                if lastCount < len(rows):
                    sameCount = 0
                    lastCount = len(rows)
                if sameCount > 4:
                    break
                random_sleep(driver)
        body = html.fromstring(driver.page_source, "lxml")

        stores = []
        for item in body.xpath(itemXpath):
            contents = item.xpath('.//div[@class="content"]/text()')
            if len(contents) == 0:
                continue
            stores.append(contents)
        return stores
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
        log.info(f"address err: {e}")
        pass
    return MISSING, MISSING, MISSING, MISSING


def fetch_data():
    stores = fetch_stores()
    log.info(f"Total stores = {len(stores)}")

    country_code = "US"
    location_type = MISSING
    latitude = "<INACCESSIBLE>"
    longitude = "<INACCESSIBLE>"

    for store in stores:
        location_name = store[0].replace("\\xa", "").strip()
        raw_address = store[1].replace("\\xa", "").strip()
        hours_of_operation = store[2].replace("\\xa", "").strip()

        if "mon -" in raw_address.lower() or "mon-" in raw_address.lower():
            hoo = raw_address
            raw_address = hours_of_operation
            hours_of_operation = hoo

        phone = get_phone(store[3])
        street_address, city, state, zip_postal = get_address(raw_address)
        store_number = (
            f"{location_name}_{zip_postal}".lower()
            .replace(" ", "_")
            .replace("_" + MISSING.lower(), "")
        )

        yield SgRecord(
            locator_domain="mobilekangaroo.com",
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
    log.info(f"Start crawling {website} ...")
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
