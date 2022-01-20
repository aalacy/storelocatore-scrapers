from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests
import re
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from sgselenium import SgSelenium
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
import time
from sgscrape.sgpostal import parse_address_intl
import ssl
from sgzip.dynamic import SearchableCountries, DynamicZipSearch

try:
    _create_unverified_https_context = (
        ssl._create_unverified_context
    )  # Legacy Python that doesn't verify HTTPS certificates by default
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context  # Handle target environment that doesn't support HTTPS verification

DOMAIN = "iga.com.au"
BASE_URL = "https://www.iga.com.au/"
LOCATION_URL = "https://www.iga.com.au/stores/#view=storelocator"
HEADERS = {
    "Accept": "application/json, text/plain, */*",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36",
    "Accept-Encoding": "gzip, deflate, sdch",
    "Accept-Language": "en-US,en;q=0.8",
    "Upgrade-Insecure-Requests": "1",
    "Cache-Control": "max-age=0",
    "Connection": "keep-alive",
}
log = sglog.SgLogSetup().get_logger(logger_name=DOMAIN)

session = SgRequests()

MISSING = "<MISSING>"


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


def handle_missing(field):
    if field is None or (isinstance(field, str) and len(field.strip()) == 0):
        return "<MISSING>"
    return field


def parse_hours(table):
    data = table.find("tbody")
    days = data.find_all("td", {"class": "c-hours-details-row-day"})
    hours = data.find_all("td", {"class": "c-hours-details-row-intervals"})
    hoo = []
    for i in range(len(days)):
        hours_formated = "{}: {}".format(days[i].text, hours[i].text)
        hoo.append(hours_formated)
    return ", ".join(hoo)


def get_latlong(url):
    latlong = re.search(r"lat=(-?[\d]*\.[\d]*)\&lng=(-[\d]*\.[\d]*)", url)
    if not latlong:
        return "<MISSING>", "<MISSING>"
    return latlong.group(1), latlong.group(2)


def wait_load(driver, wait, number=0):
    number += 1
    if wait == "STORE":
        try:
            WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.ID, "sf-stores-list"))
            )
        except:
            driver.refresh()
            if number < 3:
                log.info(f"Try to Refresh for ({number}) times")
                return wait_load(driver, wait, number)
    else:
        try:
            WebDriverWait(driver, 5).until(
                EC.presence_of_element_located(
                    (By.XPATH, '//*[@id="sf-location-search"]')
                )
            )
        except:
            driver.delete_all_cookies()
            driver.refresh()
            if number < 3:
                log.info(f"Try to Refresh for ({number}) times")
                return wait_load(driver, wait, number)
    return driver


def fetch_data():
    log.info("Fetching store_locator data")
    driver = SgSelenium().chrome()
    search = DynamicZipSearch(
        country_codes=[SearchableCountries.AUSTRALIA],
        max_search_distance_miles=20,
        max_search_results=10,
    )
    driver.get(LOCATION_URL)
    for zipcode in search:
        driver = wait_load(driver, "BASE")
        input = driver.find_element_by_xpath('//*[@id="sf-location-search"]')
        input.send_keys(zipcode)
        time.sleep(0.5)
        try:
            WebDriverWait(driver, 5).until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, "div.autocomplete-suggestions > div")
                )
            )
        except:
            input.clear()
            continue
        driver.find_element_by_css_selector(
            "div.autocomplete-suggestions > div"
        ).click()
        driver = wait_load(driver, "STORE")
        data = (
            bs(driver.page_source, "lxml")
            .find("div", {"id": "sf-stores-list"})
            .find_all("li")
        )
        log.info(f"Found {len(data)} Locations at {zipcode}")
        for row in data:
            location_name = row.find("span", {"class": "sf-storename"}).text.strip()
            raw_address = (
                row.find("p", {"class": "sf-storeaddress"})
                .get_text(strip=True, separator=",")
                .replace("\n", ",")
            )
            street_address, city, state, zip_postal = getAddress(raw_address)
            country_code = "AU"
            store_number = row["data-storeid"]
            try:
                phone = row.find(
                    "a", {"class": "sf-phone sf-contact-line"}
                ).text.strip()
            except:
                phone = MISSING
            location_type = MISSING
            hoo_content = row.find("div", {"class": "sf-storehours"})
            if not hoo_content:
                hours_of_operation = MISSING
            else:
                hours_of_operation = (
                    row.find("div", {"class": "sf-storehours"})
                    .find("table")
                    .get_text(strip=True, separator=",")
                    .replace("Opening Hours,", "")
                    .replace("day,", "day: ")
                )
            latitude = row["data-latitude"]
            longitude = row["data-longitude"]
            search.found_location_at(latitude, longitude)
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
        driver.find_element_by_xpath('//*[@id="sf-location-change"]').click()
        time.sleep(0.5)
    driver.quit()


def scrape():
    log.info("start {} Scraper".format(DOMAIN))
    count = 0
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {
                    SgRecord.Headers.STORE_NUMBER,
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
