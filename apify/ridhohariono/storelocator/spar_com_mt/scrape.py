from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from sgselenium import SgSelenium
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
import re
import ssl
from sgscrape.sgpostal import parse_address_intl


try:
    _create_unverified_https_context = (
        ssl._create_unverified_context
    )  # Legacy Python that doesn't verify HTTPS certificates by default
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context  # Handle target environment that doesn't support HTTPS verification

DOMAIN = "spar.com.mt"
BASE_URL = "https://spar.com.mt/"

log = sglog.SgLogSetup().get_logger(logger_name=DOMAIN)
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


def get_latlong(url):
    latlong = re.search(r"(-?[\d]*\.[\d]*)%2C(-?[\d]*\.[\d]*)", url)
    if not latlong:
        return MISSING, MISSING
    return latlong.group(1), latlong.group(2)


def fetch_data():
    log.info("Fetching store_locator data")
    driver = SgSelenium().chrome()
    driver.get(
        "https://www.google.com/maps/d/u/3/embed?mid=1kehyqKYdh70CKXeXQhs-cBmrLdfbnxIc&z=11"
    )
    WebDriverWait(driver, 30).until(
        EC.presence_of_element_located(
            (By.CLASS_NAME, "i4ewOd-pzNkMb-ornU0b-b0t70b-Bz112c")
        )
    )
    driver.find_element_by_class_name("i4ewOd-pzNkMb-ornU0b-b0t70b-Bz112c").click()
    single_store = driver.find_elements_by_class_name("HzV7m-pbTTYe-ibnC6b-V67aGc")
    for row in single_store:
        driver.execute_script("arguments[0].click();", row)
        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located(
                (By.CLASS_NAME, "fO2voc-jRmmHf-MZArnb-Q7Zjwb")
            )
        )
        location_name = row.find_element_by_xpath(
            '//*[@id="featurecardPanel"]/div/div/div[4]/div[1]/div[1]/div[2]'
        ).text.strip()
        raw_address = row.find_element_by_xpath(
            '//*[@id="featurecardPanel"]/div/div/div[4]/div[2]/div[2]'
        ).text.strip()
        street_address, city, state, zip_postal = getAddress(raw_address)
        phone = row.find_element_by_xpath(
            '//*[@id="featurecardPanel"]/div/div/div[4]/div[2]/div[3]'
        ).text.strip()
        if DOMAIN in phone:
            phone = "+356 2226 8888"
        hours_of_operation = (
            row.find_element_by_xpath(
                '//*[@id="featurecardPanel"]/div/div/div[4]/div[1]/div[2]/div[2]'
            )
            .text.replace("\n", ",")
            .replace("Opening Hours :", "")
            .strip()
        )
        latitude, longitude = get_latlong(driver.current_url)
        country_code = "MT"
        log.info("Append {} => {}".format(location_name, street_address))
        yield SgRecord(
            locator_domain=DOMAIN,
            page_url=BASE_URL,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=zip_postal,
            country_code=country_code,
            store_number=MISSING,
            phone=phone,
            location_type=MISSING,
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=hours_of_operation,
            raw_address=raw_address,
        )
    driver.quit()


def scrape():
    log.info("Start {} Scraper".format(DOMAIN))
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
