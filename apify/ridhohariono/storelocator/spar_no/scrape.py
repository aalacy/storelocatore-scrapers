import re
from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgpostal import parse_address_intl
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from sgselenium import SgSelenium
import ssl

try:
    _create_unverified_https_context = (
        ssl._create_unverified_context
    )  # Legacy Python that doesn't verify HTTPS certificates by default
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context  # Handle target environment that doesn't support HTTPS verification

DOMAIN = "spar.no"
BASE_URL = "https://www.spar.no/"
LOCATION_URL = "https://spar.no/finn-butikk"
HEADERS = {
    "Accept": "application/json, text/plain, */*",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36",
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
    req = session.get(url, headers=HEADERS)
    soup = bs(req.content, "lxml")
    return soup


def wait_load(driver, number=0):
    number += 1
    try:
        WebDriverWait(driver, 5).until(
            EC.presence_of_element_located(
                (By.XPATH, '//*[@id="maincontent"]/div[2]/div[2]/aside/div/nav/ul')
            )
        )
    except:
        driver.refresh()
        if number < 3:
            log.info(f"Try to Refresh for ({number}) times")
            return wait_load(driver, number)
    return driver


def fetch_data():
    log.info("Fetching store_locator data")
    driver = SgSelenium().chrome()
    driver.get(LOCATION_URL)
    wait_load(driver)
    soup = bs(driver.page_source, "lxml")
    content = soup.find_all(
        "a",
        {
            "class": "ws-find-store-navigation__button ws-find-store-navigation__button--level-2"
        },
    )
    actions = ActionChains(driver)
    for row in content:
        element = ""
        child = ""
        button = ""
        page_url = BASE_URL + row["href"]
        store = pull_content(page_url).find("div", {"class": "storepage"})
        if not store:
            element = driver.find_element_by_xpath(
                '//a[@href="'
                + row["href"]
                + '"]/ancestor::li[contains(concat(" ", @class, " "), "ws-find-store-navigation__list-item--level-0")]'
            )
            child = element.find_element_by_xpath(
                '//a[@href="'
                + row["href"]
                + '"]/ancestor::li[contains(concat(" ", @class, " "), "ws-find-store-navigation__list-item--level-1")]'
            )
            button = child.find_element_by_class_name(
                "ws-find-store-navigation__button--info"
            )
            actions.move_to_element(element)
            actions.click(element)
            actions.move_to_element(child)
            actions.click(child)
            actions.move_to_element(button)
            actions.click(button)
            actions.perform()
            try:
                WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located(
                        (
                            By.CLASS_NAME,
                            "ngr-modal--store-info",
                        )
                    )
                )
            except:
                button.click()
            store_info = bs(
                driver.find_element_by_class_name(
                    "ngr-modal--store-info"
                ).get_attribute("innerHTML"),
                "lxml",
            )
            driver.find_element_by_class_name("ngr-modal__close").click()
            location_name = store_info.find(
                "a", {"class": "ws-store-info__store-link"}
            ).text.strip()
            raw_address = store_info.find("address").get_text(strip=True, separator=",")
            street_address, city, state, zip_postal = getAddress(raw_address)
            phone = store_info.find(
                "dd", {"class": "ws-store-info__list-value--phone"}
            ).text.strip()
            hours_of_operation = re.sub(
                r"(\D),",
                r"\1:",
                store_info.find(
                    "div", {"class": "ws-store-info__opening-hours"}
                ).get_text(strip=True, separator=","),
            )
            latitude = MISSING
            longitude = MISSING
        else:
            location_name = store.find("h1", {"itemprop": "name"}).text.strip()
            raw_address = store.find("address").get_text(strip=True, separator=",")
            street_address, city, state, zip_postal = getAddress(raw_address)
            phone = store.find("a", {"itemprop": "telephone"}).text.strip()
            country_code = "NO"
            latitude = store.find("meta", {"itemprop": "latitude"})["content"].replace(
                ",", "."
            )
            longitude = store.find("meta", {"itemprop": "longitude"})[
                "content"
            ].replace(",", ".")
            hours_of_operation = re.sub(
                r"(\D),",
                r"\1:",
                store.find("dl", {"class": "openinghours"}).get_text(
                    strip=True, separator=","
                ),
            )
        country_code = "NO"
        store_number = MISSING
        location_type = MISSING
        log.info("Append {} => {}".format(location_name, street_address))
        yield SgRecord(
            locator_domain=DOMAIN,
            page_url=page_url,
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
