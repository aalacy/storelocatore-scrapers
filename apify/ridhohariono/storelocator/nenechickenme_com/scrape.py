from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgselenium import SgSelenium
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait as wait
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

DOMAIN = "nenechickenme.com"
LOCATION_URL = "http://www.nenechickenme.com"
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
    soup = pull_content(LOCATION_URL)
    stores = re.sub(
        r"\|\|Follow us on Instagram.*|\|\|WhatsApp 0585916499\|\|",
        "",
        soup.select_one("div.photo-text div.body-text")
        .get_text(strip=True, separator="||")
        .replace("||COMING SOON! @", "@ COMING SOON!")
        .replace("||Call", "")
        .replace("/Whatsapp", "||"),
    ).split("@")[1:]
    driver = SgSelenium().chrome()
    driver.get(LOCATION_URL)
    driver.implicitly_wait(10)
    iframes = driver.find_elements_by_css_selector("div.map-component--inner iframe")
    num = 0
    for iframe in iframes:
        info = stores[num].split("||")
        if "COMING SOON" in info[0].strip():
            continue
        driver.execute_script("arguments[0].scrollIntoView(true);", iframe)
        driver.switch_to.frame(iframe)
        wait(driver, 10).until(
            EC.presence_of_element_located(
                (
                    By.XPATH,
                    '//*[@id="mapDiv"]/div/div/div[4]/div/div/div/div/div[1]/div[2]',
                )
            )
        )
        store_info = (
            bs(driver.page_source, "lxml")
            .find(id="mapDiv")
            .find("div", {"class": "place-card place-card-large"})
        )
        location_name = store_info.find("div", {"class": "place-name"}).text.strip()
        raw_address = (
            store_info.find("div", {"class": "address"}).text.replace("\n", ",").strip()
        )
        street_address, city, state, zip_postal = getAddress(raw_address)
        if street_address == MISSING:
            street_address = raw_address.split("-")[1].strip()
        phone = info[-1].strip()
        country_code = "UAE"
        hours_of_operation = MISSING
        location_type = MISSING
        store_number = MISSING
        latlong = (
            store_info.find("div", {"jsaction": "placeCard.directions"})
            .find("a")["href"]
            .split("@")[1]
            .split(",16z/")[0]
            .split(",")
        )
        latitude, longitude = latlong
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
        driver.switch_to.default_content()
        num += 1
    driver.quit()


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
