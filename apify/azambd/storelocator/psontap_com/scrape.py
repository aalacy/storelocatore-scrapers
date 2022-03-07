import ssl
import random
import json
import time
from lxml import html

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from sglogging import sglog
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgselenium.sgselenium import SgChrome

ssl._create_default_https_context = ssl._create_unverified_context

DOMAIN = "psontap_com"

website = "https://www.psontap.com"
MISSING = SgRecord.MISSING

user_agent = (
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:78.0) Gecko/20100101 Firefox/78.0"
)

log = sglog.SgLogSetup().get_logger(logger_name=DOMAIN)


def driver_sleep(driver, time=2):
    try:
        WebDriverWait(driver, time).until(
            EC.presence_of_element_located((By.ID, MISSING))
        )
    except Exception as e:
        log.info(f"No Sleep Time: {e}")
        pass


def random_sleep(driver, start=5, limit=6):
    driver_sleep(driver, random.randint(start, start + limit))


def fetch_stores():
    driver = SgChrome(
        user_agent=user_agent,
        is_headless=True,
    ).driver()

    driver.get(f"{website}/our-locations")
    random_sleep(driver, 10)
    body = html.fromstring(driver.page_source, "lxml")
    stores = []
    jsonDatas = body.xpath('//script[contains(@type, "application/ld+json")]/text()')

    for jsonData in jsonDatas:
        if '"openingHours"' in jsonData:
            store = {"latitude": MISSING, "longitude": MISSING}

            data = json.loads(jsonData)
            address = data["address"]
            store["street_address"] = address["streetAddress"]
            store["city"] = address["addressLocality"]
            store["state"] = address["addressRegion"]
            store["zip_postal"] = address["postalCode"]
            store["phone"] = address["telephone"]
            store["hoo"] = "; ".join(data["openingHours"])
            store_number = address["email"].split("@")[0].replace("PS", "")
            store["store_number"] = store_number
            store["page_url"] = f"{website}/PS-{store_number}"
            stores.append(store)
    log.debug(f"Total stores = {len(stores)}")

    for store in stores:
        page_url = store["page_url"]
        log.debug(f"Scrapping {page_url} ...")
        driver.get(page_url)
        random_sleep(driver, 10)
        body = html.fromstring(driver.page_source, "lxml")
        store["location_name"] = body.xpath(".//h1/text()")[0]

        mapAs = body.xpath(".//a[contains(@href,'google.com/maps/@')]/@href")
        if len(mapAs) > 0:
            parts = mapAs[0].split("maps/@")[1].split(",")
            store["latitude"] = parts[0]
            store["longitude"] = parts[1]

    driver.quit()
    return stores


def fetch_data():
    stores = fetch_stores()
    log.info(f"Total stores = {len(stores)}")
    for store in stores:
        store_number = store["store_number"]
        page_url = store["page_url"]
        location_name = store["location_name"]
        location_type = MISSING
        street_address = store["street_address"]
        city = store["city"]
        zip_postal = store["zip_postal"]
        state = store["state"]
        country_code = "USA"
        phone = store["phone"]
        latitude = store["latitude"]
        longitude = store["longitude"]
        hours_of_operation = store["hoo"]
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
    result = fetch_data()
    with SgWriter(deduper=SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        for rec in result:
            writer.write_row(rec)
    end = time.time()
    log.info(f"Scrape took {end-start} seconds.")


if __name__ == "__main__":
    scrape()
