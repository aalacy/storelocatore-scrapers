import json
import random
import time
from sglogging import SgLogSetup
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgselenium import SgChrome
from sgscrape.pause_resume import CrawlStateSingleton
from sgpostal.sgpostal import parse_address_intl
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgzip.dynamic import SearchableCountries, DynamicZipSearch
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

import ssl

ssl._create_default_https_context = ssl._create_unverified_context

log = SgLogSetup().get_logger("burgerking")

website = "https://www.burgerking.in"
page_url = "https://www.burgerking.in/store-locator"
json_url = "/api/v1/outlet/getOutlet"
MISSING = SgRecord.MISSING


def driver_sleep(driver, time=2):
    try:
        WebDriverWait(driver, time).until(
            EC.presence_of_element_located((By.ID, MISSING))
        )
    except Exception:
        pass


def random_sleep(driver, start=1, limit=2):
    driver_sleep(driver, random.randint(start, start + limit))


def fetch_stores(driver, alert=False):
    if not alert:
        try:
            WebDriverWait(driver, 10).until(EC.alert_is_present())
            driver.switch_to.alert.accept()
        except Exception as e:
            log.info(f"Error #L50: {e}")
            pass

    try:
        driver.wait_for_request(json_url, 30)
    except:
        pass

    stores = []

    count = 0
    while True:
        count = count + 1
        data = [rr.response for rr in driver.requests if json_url in rr.url]
        random_sleep(driver, 1)

        if len(data) > 1 and data[1]:
            stores = json.loads(data[-1].body)["content"]
            break
        if count == 4:
            break
    return stores


def get_address(raw_address):
    try:
        if raw_address and raw_address != MISSING:
            raw_address = raw_address.split(":")[0].replace("-", " ").replace("–", " ")
            data = parse_address_intl(raw_address + ", India")
            street_address = data.street_address_1
            if data.street_address_2:
                street_address = street_address + " " + data.street_address_2
            city = data.city
            state = data.state
            zip_postal = data.postcode
            if city:
                if city == "City":
                    city = raw_address.split(city)[-1].strip()
                city = " ".join(
                    [
                        cc.strip()
                        for cc in city.split()
                        if cc.strip() and not cc.isdigit()
                    ]
                )
                if "Mcdoanlds" in city or "Arneja" in city or "Sec" in city:
                    city = ""
                if "Up" == city:
                    city = ""
            return street_address, city, state, zip_postal
    except Exception as e:
        log.info(f"Address Missing: {e}")
        pass
    return MISSING, MISSING, MISSING, MISSING


def fetch_data(driver):
    store_numbers = []
    close_stores = 0

    try:
        driver.get(page_url)
        random_sleep(driver, 5)
    except:
        pass
    try:
        WebDriverWait(driver, 10).until(EC.alert_is_present())
        driver.switch_to.alert.accept()
    except Exception as e:
        log.info(f"Error #L113: {e}")
        pass

    driver.get(page_url)
    stores = fetch_stores(driver)

    for store in stores:
        store_number = store["outlet_id"]
        if store["is_closed"]:
            close_stores = close_stores + 1

        store_numbers.append(store_number)

        location_type = MISSING
        location_name = store["outlet_name"]
        latitude = store["lat"]
        longitude = store["long"]
        phone = store["phone_no"]
        raw_address = store["address"]
        street_address, city, state, zip_postal = get_address(raw_address)
        hours_of_operation = f"{store['opens_at']}-{store['closes_at']}"
        if "---" in hours_of_operation:
            hours_of_operation = MISSING

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
            country_code="IN",
            phone=phone,
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=hours_of_operation,
            raw_address=raw_address,
        )

    log.info(
        f"Total stores from start = {len(stores) - close_stores} closed={close_stores}"
    )

    count = 0
    zip_codes = DynamicZipSearch(
        country_codes=[SearchableCountries.INDIA], expected_search_radius_miles=500
    )

    for zip_code in zip_codes:
        count = count + 1
        input_search = driver.find_element_by_xpath(
            "//input[contains(@class, 'location-search-input')]"
        )
        try:
            input_search.clear()
        except Exception as e:
            log.info(f"Error #L162: {e}")
            pass
        try:
            driver.find_element_by_xpath(
                "//div[contains(@class, 'search-autocompletenomap__clear')]"
            ).click()
        except Exception as e:
            log.info(f"Error #L167: {e}")
            pass
        random_sleep(driver, 2)
        try:
            input_search.send_keys(zip_code)
            random_sleep(driver, 2)
            input_search.send_keys(Keys.ENTER)
            stores = fetch_stores(driver, True)
        except Exception as e:
            log.info(f"Error #L184: {e}")
            continue

        for store in stores:
            store_number = store["outlet_id"]
            if store_number in store_numbers:
                continue
            store_numbers.append(store_number)
            if store["is_closed"]:
                close_stores = close_stores + 1

            location_name = store["outlet_name"]
            latitude = store["lat"]
            longitude = store["long"]
            phone = store["phone_no"]
            raw_address = f"{store['address']}"
            street_address, city, state, zip_postal = get_address(raw_address)
            hours_of_operation = f"{store['opens_at']}-{store['closes_at']}"
            if "---" in hours_of_operation:
                hours_of_operation = MISSING

            yield SgRecord(
                locator_domain=website,
                store_number=store_number,
                page_url=page_url,
                location_name=location_name,
                street_address=street_address,
                city=city,
                zip_postal=zip_postal,
                state=state,
                country_code="IN",
                phone=phone,
                latitude=latitude,
                longitude=longitude,
                hours_of_operation=hours_of_operation,
                raw_address=raw_address,
            )
        log.info(
            f"{count}. From {zip_code} stores = {len(stores)}, total stores = {len(store_numbers)-close_stores} closed={close_stores}"
        )

    log.info(f"total stores = {len(store_numbers)}")
    log.info(f"Closed stores = {close_stores}")


def scrape():
    log.info(f"Start Crawling {website} ...")
    start = time.time()
    CrawlStateSingleton.get_instance().save(override=True)
    with SgChrome() as driver:
        with SgWriter(
            deduper=SgRecordDeduper(
                RecommendedRecordIds.StoreNumberId, duplicate_streak_failure_factor=-1
            )
        ) as writer:
            for rec in fetch_data(driver):
                writer.write_row(rec)

    end = time.time()
    log.info(f"Scrape took {end-start} seconds.")


if __name__ == "__main__":
    scrape()
