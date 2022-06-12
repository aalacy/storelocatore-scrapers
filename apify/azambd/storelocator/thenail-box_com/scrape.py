from lxml import html
import time
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
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context

DOMAIN = "thenail-box.com"
website = "https://www.thenail-box.com"
MISSING = "<MISSING>"

log = sglog.SgLogSetup().get_logger(logger_name=DOMAIN)


def driverSleep(driver, time=2):
    try:
        WebDriverWait(driver, time).until(
            EC.presence_of_element_located((By.ID, MISSING))
        )
    except Exception as e1:
        log.info(f"NO need sleep time {e1}")
        pass


def driverWaitTillUrl(driver, text, totalDelay=240):
    delay = 2
    while delay < totalDelay:
        driverSleep(driver)
        log.debug(f"Waiting to load location-details-window, delay={delay * 2}s")

        if text in driver.page_source:
            return
        delay = delay + 2
    raise Exception("Can't overcome CF")


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
            try:
                log.debug("find pop up")
                time.sleep(20)
                button = driver.find_element_by_xpath(
                    '//div[contains(@title, "Back to site")]'
                )
                driver.execute_script("arguments[0].click();", button)
                log.debug("click on cross")
            except Exception as e:
                log.info(f"Failed Driver {e}")
                pass

            driverSleep(driver, 3)
            driver.find_element_by_xpath('//p[contains(text(), "LOCATIONS")]').click()
            log.debug("click on LOCATIONS")
            driverSleep(driver, 40)
            driver.switch_to.frame(
                driver.find_element_by_xpath('//iframe[@title="Located Map"]')
            )
            log.debug("waiting for location loading")
            driverSleep(driver, 20)
            body = html.fromstring(driver.page_source, "lxml")
            stores = body.xpath('//div[@id="location-cards"]//div[@class="card-body"]')
            driver.quit()
            return stores

        except Exception as e:
            log.error(f"Error loading : {e}")
            driver.quit()
            if x == 3:
                raise Exception(
                    "Make sure this ran with a Proxy, will fail without one"
                )
            continue
    return []


def fetchData():
    stores = fetchStores()
    log.info(f"Total stores = {len(stores)}")
    for store in stores:
        raw_address = store.xpath(".//h5/following-sibling::div/div/text()")[0].strip()
        addressParts = raw_address.split(", ")

        location_type = MISSING
        store_number = MISSING
        latitude = MISSING
        longitude = MISSING

        page_url = website
        location_name = store.xpath(".//h5/text()")[0]
        street_address = addressParts[0]
        city = addressParts[1]
        zip_postal = addressParts[2].split()[-1].strip()
        state = addressParts[2].split()[0].strip()
        country_code = addressParts[-1]
        raw_address = raw_address.replace(f", {country_code}", "")
        phone = store.xpath('.//a[contains(@href, "tel")]/text()')[0].strip()

        hoo = store.xpath('.//div[contains(text(), "MON-FRI")]/text()')
        hoo = [day.strip() for day in hoo if day.strip()]
        hours_of_operation = " ".join(hoo) if hoo else "<MISSING>"
        raw_address = raw_address.replace(f", {country_code}", "")

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
