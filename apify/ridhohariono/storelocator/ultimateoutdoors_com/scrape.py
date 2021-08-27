from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from sgselenium import SgSelenium
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgpostal import parse_address_intl
import ssl

try:
    _create_unverified_https_context = (
        ssl._create_unverified_context
    )  # Legacy Python that doesn't verify HTTPS certificates by default
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context  # Handle target environment that doesn't support HTTPS verification

DOMAIN = "ultimateoutdoors.com"
BASE_URL = "https://ultimateoutdoors.com/"
LOCATION_URL = "https://www.ultimateoutdoors.com/google/store-locator?search=showall"
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


def wait_load(driver):
    try:
        WebDriverWait(driver, 5).until(
            lambda driver: driver.execute_script("return jQuery.active == 0")
        )
        WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.CLASS_NAME, "store-list"))
        )
    except:
        driver.refresh()


def fetch_data():
    log.info("Fetching store_locator data")
    driver = SgSelenium().chrome()
    driver.get(LOCATION_URL)
    wait_load(driver)
    soup = bs(driver.page_source, "lxml")
    driver.quit()
    content = soup.find("ul", {"class": "store-list"})
    store_info = content.find_all("li", {"class": "group"})
    for row in store_info:
        info = row.find("div", {"class": "store-details"})
        location_name = info.find("h3").text.strip()
        raw_address = ",".join(
            [addr.text for addr in info.find_all("p", {"class": "storeAddress"})]
        )
        addr = info.find_all("p", {"class": "storeAddress"})
        street_address = addr[0].text.strip()
        city = location_name.split(" | ")[1].strip()
        state = MISSING
        zip_postal = addr[1].text.strip()
        phone = info.find("p", {"class": "tel"}).text
        hours_of_operation = (
            row.find("table", {"class": "storefinder_opening"})
            .find_all("tr")[1]
            .get_text(strip=True, separator=",")
        )
        store_number = row["data-id"]
        country_code = "GB"
        location_type = location_name.split(" | ")[0].strip()
        latitude = MISSING
        longitude = MISSING
        log.info("Append {} => {}".format(location_name, street_address))
        yield SgRecord(
            locator_domain=DOMAIN,
            page_url=LOCATION_URL,
            location_name=location_name,
            street_address=street_address.strip(),
            city=city.strip(),
            state=state.strip(),
            zip_postal=zip_postal.strip(),
            country_code=country_code,
            store_number=store_number,
            phone=phone.strip(),
            location_type=location_type,
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=hours_of_operation,
            raw_address=raw_address,
        )


def scrape():
    log.info("start {} Scraper".format(DOMAIN))
    count = 0
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {
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
