from lxml import html
import time
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

try:
    _create_unverified_https_context = (
        ssl._create_unverified_context
    )  # Legacy Python that doesn't verify HTTPS certificates by default
except AttributeError:
    pass
else:
    # Handle target environment that doesn't support HTTPS verification
    ssl._create_default_https_context = _create_unverified_https_context

DOMAIN = "eescodist.com"
website = "https://buy.eescodist.com"
MISSING = SgRecord.MISSING
startUrl = f"{website}/content/branch-locator"

log = sglog.SgLogSetup().get_logger(logger_name=DOMAIN)


def driverSleep(driver, time=2):
    try:
        WebDriverWait(driver, time).until(
            EC.presence_of_element_located((By.ID, MISSING))
        )
    except Exception as e1:
        log.info(f"No Sleep time: {e1}")
        pass


def randomSleep(driver, start=5, limit=6):
    driverSleep(driver, random.randint(start, start + limit))


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

            driver.get(website)
            randomSleep(driver, 20)

            driver.get(startUrl)
            randomSleep(driver, 20)
            body = html.fromstring(driver.page_source, "lxml")
            driver.quit()
            stores = body.xpath('//div[contains(@class, "col three")]/p')[2:]
            if len(stores) == 0:
                continue
            else:
                return stores
        except Exception as e:
            log.error(f"Error loading : {e}")
            driver.quit()
            if x == 2:
                raise Exception(
                    "Make sure this ran with a Proxy, will fail without one"
                )
            continue
    return []


def fetchData():
    stores = fetchStores()
    log.info(f"Total stores = {len(stores)}")
    for store in stores:
        store_number = MISSING
        location_name = MISSING
        location_type = MISSING
        hours_of_operation = MISSING

        page_url = startUrl
        raw_data = store.xpath("text()")
        street_address = raw_data[0].strip()
        city = raw_data[1].split(", ")[0].strip()
        state = raw_data[1].split(", ")[-1].split()[0].strip()
        zip_postal = raw_data[1].split(", ")[-1].split()[-1].strip()
        country_code = "US"
        phone = [e for e in raw_data if "Phone" in e]
        phone = phone[0].split(":")[-1].strip() if phone else MISSING

        mapUrl = store.xpath('.//a[contains(@href, "/@")]/@href')
        latitude = MISSING
        longitude = MISSING

        if mapUrl:
            mapUrl = mapUrl[0].split("/@")[-1].split(",")[:2]
            latitude = mapUrl[0]
            longitude = mapUrl[1]

        raw_address = f"{street_address} {city}, {state} {zip_postal}"

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
    return []


def scrape():
    log.info(f"Start scrapping {website} ...")
    start = time.time()
    result = fetchData()
    with SgWriter(
        deduper=SgRecordDeduper(RecommendedRecordIds.PhoneNumberId)
    ) as writer:
        for rec in result:
            writer.write_row(rec)
    end = time.time()
    log.info(f"Scrape took {end-start} seconds.")


if __name__ == "__main__":
    scrape()
