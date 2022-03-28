import time
from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests
from sglogging import sglog
from sgselenium import SgSelenium
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from selenium.webdriver.common.by import By
from sgscrape.sgpostal import parse_address_intl
import re
import ssl

try:
    _create_unverified_https_context = (
        ssl._create_unverified_context
    )  # Legacy Python that doesn't verify HTTPS certificates by default
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context  # Handle target environment that doesn't support HTTPS verification

DOMAIN = "drmartens.com"
LOCATION_URL = "https://www.drmartens.com/intl/en/store-finder"
API_URL = "https://www.drmartens.com/intl/en/store-finder?q=london&page={}"
HEADERS = {
    "Accept": "application/json, text/plain, */*",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36",
}
MISSING = "<MISSING>"
log = sglog.SgLogSetup().get_logger(logger_name=DOMAIN)

session = SgRequests()


def getAddress(raw_address):
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
        log.info(f"No valid address {e}")
        pass
    return MISSING, MISSING, MISSING, MISSING


def pull_content(url):
    log.info("Pull content => " + url)
    soup = bs(session.get(url, headers=HEADERS).content, "lxml")
    return soup


def fetch_data():
    log.info("Fetching store_locator data")
    driver = SgSelenium().chrome()
    driver.get(LOCATION_URL)
    driver.implicitly_wait(10)
    js_string = 'var element = document.getElementById("bfx-cc-wrapper-expanded");element.remove();'
    try:
        driver.execute_script(js_string)
    except:
        pass
    search_from = driver.find_element(By.ID, "storelocator-query")
    try:
        driver.find_element(By.ID, "bfx-wm-close-button").click()
    except:
        pass
    search_from.send_keys("london")
    try:
        driver.find_element(
            By.XPATH, '//*[@id="storeFinderForm"]/div/span/button'
        ).click()
    except:
        try:
            driver.execute_script(js_string)
            driver.find_element(
                By.XPATH, '//*[@id="storeFinderForm"]/div/span/button'
            ).click()
        except:
            pass
    driver.implicitly_wait(10)
    num = 1
    while True:
        log.info(f"Get all locations in page ({num})")
        driver.implicitly_wait(5)
        stores = driver.find_elements(
            By.XPATH, '//*[@id="storeFinder"]/div/div[2]/div/div/div[2]/div[1]/ul/li'
        )
        driver.execute_script("return arguments[0].scrollIntoView(true);", search_from)
        for store in stores:
            try:
                store.click()
            except:
                store.find_element(By.CLASS_NAME, "js-select-store-label").click()
            time.sleep(1)
            driver.implicitly_wait(5)
            info = driver.find_element(By.CLASS_NAME, "store__finder--details-info")
            location_name = info.find_element(
                By.CLASS_NAME, "js-store-displayName"
            ).text.strip()
            address = (
                info.find_element(By.CLASS_NAME, "info__address")
                .text.replace("\n", ",")
                .strip()
                .split(",")
            )
            get_phone = "".join(re.findall(r"\d+", address[-1]))
            if len(get_phone) < 8:
                phone = MISSING
                raw_address = ", ".join(address).strip()
            else:
                raw_address = ", ".join(address[:-1]).strip()
                phone = (
                    (
                        re.sub(
                            r"Tel.?|Tél.?|:|Phone|Llamados y Whatsapp|Llamados",
                            "",
                            address[-1],
                            flags=re.IGNORECASE,
                        )
                        .replace("\u202c", "")
                        .strip()
                    )
                    .split("/")[0]
                    .strip()
                )
            street_address, city, state, zip_postal = getAddress(raw_address)
            country_code = MISSING
            hoo = ""
            try:
                hoo_content = driver.find_element(
                    By.CSS_SELECTOR, "div.store__finder--details-openings dl"
                )
                days = hoo_content.find_elements(By.TAG_NAME, "dt")
                hours = hoo_content.find_elements(By.TAG_NAME, "dd")
                for i in range(len(days)):
                    hoo += days[i].text.strip() + ": " + hours[i].text.strip() + ","
                hours_of_operation = hoo.rstrip(",")
            except:
                hours_of_operation = MISSING
            location_type = MISSING
            if "temporarily closed" in location_name:
                location_type = "TEMP_CLOSED"
            store_number = MISSING
            map_link = driver.find_element(
                By.XPATH, '//*[@id="store-finder-map"]/div/div/div[14]/div/a'
            ).get_attribute("href")
            latlong = map_link.split("ll=")[1].split("&z=")[0].split(",")
            latitude = latlong[0] if len(latlong[0]) > 1 else MISSING
            longitude = latlong[1] if len(latlong[1]) > 1 else MISSING
            log.info("Append {} => {}".format(location_name, street_address))
            yield SgRecord(
                locator_domain=DOMAIN,
                page_url=LOCATION_URL,
                location_name=location_name,
                street_address=street_address,
                city=city,
                state=state,
                zip_postal=zip_postal,
                country_code=country_code,
                store_number=store_number,
                phone=phone,
                location_type=location_type,
                latitude=latitude,
                longitude=longitude,
                hours_of_operation=hours_of_operation,
                raw_address=raw_address,
            )
        next_btn = driver.find_element_by_xpath(
            '//*[@id="storeFinder"]/div/div[2]/div/div/div[3]/div/button[2]'
        )
        driver.execute_script("arguments[0].scrollIntoView();", next_btn)
        if next_btn.is_enabled():
            next_btn.click()
            num += 1
            time.sleep(3)
        else:
            driver.quit()
            break


def scrape():
    log.info("start {} Scraper".format(DOMAIN))
    count = 0
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {
                    SgRecord.Headers.LOCATION_NAME,
                    SgRecord.Headers.RAW_ADDRESS,
                }
            )
        )
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


scrape()
