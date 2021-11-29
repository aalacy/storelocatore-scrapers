import time
from lxml import html

from webdriver_manager.chrome import ChromeDriverManager
from sgpostal.sgpostal import parse_address_intl
from sgselenium.sgselenium import SgChrome
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from sglogging import sglog

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID

import ssl

try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context


website = "https://www.jacknathanhealth.com"
MISSING = "<MISSING>"
CLINIC_URL = f"{website}/clinic-finder"

user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36"

log = sglog.SgLogSetup().get_logger(logger_name=website)


def getAddress(raw_address):
    if raw_address is None or raw_address == MISSING:
        return MISSING, MISSING, MISSING, MISSING
    try:
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
        log.error(f"Address Err: {e}")
        pass
    return MISSING, MISSING, MISSING, MISSING


def getAttribute(card, xpath):
    elements = card.xpath(xpath)
    if len(elements):
        return elements[0]
    return MISSING


def getLatLongFromMapUrl(page_url):
    if "/@" not in page_url:
        return MISSING, MISSING
    part = page_url.split("/@")[1]
    if "/" not in part:
        return MISSING, MISSING
    part = part.split("/")[0]
    if "," not in part:
        return MISSING, MISSING
    parts = part.split(",")
    return parts[0], parts[1]


def initiateDriver(driver=None):
    if driver is not None:
        driver.quit()

    return SgChrome(
        is_headless=True,
        user_agent=user_agent,
        executable_path=ChromeDriverManager().install(),
    ).driver()


def driverSleep(driver, time=80):
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
        driver.get(CLINIC_URL)
        driverSleep(driver)
        try:
            WebDriverWait(driver, 120).until(
                EC.frame_to_be_available_and_switch_to_it(
                    driver.find_element_by_xpath("//iframe")
                )
            )

            zoButton = driver.find_element_by_xpath("//button[@id='zoom-out-btn']")
            log.info("Zooming out to load locations on map...")
            zoButton.click()
            zoButton.click()
            zoButton.click()
            zoButton.click()
            driverSleep(driver)

            body = html.fromstring(driver.page_source, "lxml")
            cards = body.xpath("//div[@class='card-body']")

            missingLat = 0
            missingAddress = 0
            stores = []
            for card in cards:
                location_name = getAttribute(card, ".//h5/text()")
                raw_address = getAttribute(card, './/div[@class="col-12"]/text()')
                street_address, city, state, zip_postal = getAddress(raw_address)
                phone = getAttribute(card, './/a[contains(@href, "tel:")]/text()')
                page_url = getAttribute(
                    card, './/a[contains(text(), "View Website")]/@href'
                )
                latitude, longitude = getLatLongFromMapUrl(page_url)

                if latitude == MISSING:
                    missingLat = missingLat + 1
                if street_address == MISSING:
                    missingAddress = missingAddress + 1
                stores.append(
                    {
                        "page_url": page_url,
                        "location_name": location_name,
                        "street_address": street_address,
                        "city": city,
                        "zip_postal": zip_postal,
                        "state": state,
                        "phone": phone,
                        "latitude": latitude,
                        "longitude": longitude,
                        "raw_address": raw_address,
                    }
                )
            log.debug(f"Total Missing latitude = {missingLat}")
            log.debug(f"Total Missing address = {missingAddress}")
            return stores
        except Exception as e:
            log.error(f"Failed to initiate {e}")
            if x == 3:
                raise Exception(
                    "Make sure this ran with a Proxy, will fail without one"
                )
                break
            continue
    return []


def fetchData():
    stores = fetchStores()
    log.info(f"Total stores = {len(stores)}")
    for store in stores:
        store_number = MISSING
        country_code = MISSING
        location_type = MISSING
        hours_of_operation = MISSING

        page_url = store["page_url"]
        location_name = store["location_name"]
        street_address = store["street_address"]
        city = store["city"]
        zip_postal = store["zip_postal"]
        state = store["state"]
        phone = store["phone"]
        latitude = store["latitude"]
        longitude = store["longitude"]

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
        )
    return []


def scrape():
    start = time.time()
    result = fetchData()
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.PAGE_URL, SgRecord.Headers.PHONE}))
    ) as writer:
        for rec in result:
            writer.write_row(rec)
    end = time.time()
    log.info(f"Scrape took {end-start} seconds.")


if __name__ == "__main__":
    scrape()
