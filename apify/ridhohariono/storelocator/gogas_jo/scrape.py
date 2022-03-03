from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgselenium import SgSelenium
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
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


DOMAIN = "gogas.jo"
LOCATION_URL = "http://www.gogas.jo/gas-stations"
HEADERS = {
    "Accept": "*/*",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.82 Safari/537.36",
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


def pull_content(url):
    log.info("Pull content => " + url)
    HEADERS["Referer"] = url
    soup = bs(session.get(url, headers=HEADERS).content, "lxml")
    return soup


def click_and_wait_modal(driver, btn, number=0):
    number += 1
    try:
        WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.ID, "POPUPS_ROOT"))
        )
        WebDriverWait(driver, 5).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, "wix-iframe[title='Google Maps'] iframe")
            )
        )
        WebDriverWait(driver, 10).until(
            lambda driver: driver.execute_script("return document.readyState")
            == "complete"
        )
    except:
        btn.click()
        log.info(f"Try to Refresh for ({number}) times")
        return click_and_wait_modal(driver, btn, number)


def wait_gmap_iframe(driver, number=0):
    number += 1
    log.info("Wait for google maps iframe...")
    try:
        WebDriverWait(driver, 5).until(
            EC.presence_of_element_located(
                (By.XPATH, '//*[@id="map_canvas"]/div/div/div[14]/div')
            )
        )
        WebDriverWait(driver, 10).until(
            lambda driver: driver.execute_script("return document.readyState")
            == "complete"
        )
    except:
        log.info(f"Try to Refresh for ({number}) times")
        return wait_gmap_iframe(driver, number)


def close_modal(driver):
    driver.find_element_by_css_selector(
        "div#POPUPS_ROOT div[title='Back to site']"
    ).click()


def cleaner(soup):
    b = soup.find_all("p", text="\xa0")
    for i in b:
        i.decompose()
    c = soup.find_all("span", {"class": "wixGuard"})
    for i in c:
        i.decompose()
    return soup


def fetch_data():
    driver = SgSelenium().chrome()
    driver.get(LOCATION_URL)
    driver.implicitly_wait(10)
    contents = driver.find_elements_by_css_selector(
        "div[data-mode='default'] a[role='button']"
    )
    actions = ActionChains(driver)
    for btn in contents:
        actions.move_to_element(btn).perform()
        click_and_wait_modal(driver, btn)
        iframe = iframe = driver.find_element_by_css_selector(
            "wix-iframe[title='Google Maps'] iframe"
        )
        driver.switch_to.frame(iframe)
        wait_gmap_iframe(driver)
        map_link = driver.find_element_by_xpath(
            '//*[@id="map_canvas"]/div/div/div[14]/div/a'
        ).get_attribute("href")
        driver.switch_to.default_content()
        info = (
            cleaner(
                bs(
                    driver.find_element_by_xpath(
                        "//*[contains(text(), 'Tel')]/../../../../.."
                    ).get_attribute("innerHTML"),
                    "lxml",
                )
            )
            .get_text(strip=True, separator=",")
            .replace(",Customer.Service@gogas.jo", "")
            .replace("Tel:", "")
        ).split(",")
        close_modal(driver)
        location_name = btn.text.strip()
        raw_address = ", ".join(info[:-1]).replace("-,", "- ")
        _, city, state, zip_postal = getAddress(raw_address)
        street_address = raw_address.split(",")[0]
        if "Irbid" in raw_address:
            city = "Irbid"
        phone = info[-1]
        latlong = map_link.split("ll=")[1].split("&z=")[0].split(",")
        latitude = latlong[0]
        longitude = latlong[1]
        country_code = "JO"
        store_number = MISSING
        hours_of_operation = MISSING
        location_type = MISSING
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
    driver.quit()


def scrape():
    log.info("start {} Scraper".format(DOMAIN))
    count = 0
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {
                    SgRecord.Headers.LOCATION_NAME,
                    SgRecord.Headers.STREET_ADDRESS,
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
