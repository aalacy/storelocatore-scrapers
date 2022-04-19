from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgselenium import SgChrome
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from sglogging import SgLogSetup
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from webdriver_manager.chrome import ChromeDriverManager
import time
from sgpostal.sgpostal import parse_address_intl
import ssl

try:
    _create_unverified_https_context = (
        ssl._create_unverified_context
    )  # Legacy Python that doesn't verify HTTPS certificates by default
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context  # Handle target environment that doesn't support HTTPS verification

logger = SgLogSetup().get_logger("salsafrescagrill")
map_url = r"api\.maptiler\.com/tiles/v3"
locator_domain = "https://www.salsafrescagrill.com/"
base_url = "https://www.salsafrescagrill.com/locations"


def get_driver():
    return SgChrome(
        executable_path=ChromeDriverManager().install(),
        user_agent="Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:78.0) Gecko/20100101 Firefox/78.0",
        is_headless=False,
    ).driver()


def fetch_data():
    driver = get_driver()
    driver.get(base_url)
    WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.XPATH, "//iframe"))
    )
    iframe = driver.find_element_by_xpath("//iframe")
    time.sleep(5)
    driver.switch_to.frame(iframe)
    driver.find_element_by_css_selector(
        "button.maplibregl-ctrl-fullscreen.mapboxgl-ctrl-fullscreen"
    ).click()
    time.sleep(2)
    for marker in driver.find_elements_by_css_selector('div[aria-label="Map marker"]'):
        driver.execute_script("arguments[0].click();", marker)
        time.sleep(1)
        info = driver.find_element_by_css_selector("div.mapboxgl-popup-content")
        raw_address = info.find_element_by_css_selector("p.popup-address").text.strip()
        addr = parse_address_intl(raw_address)
        street_address = addr.street_address_1
        if addr.street_address_2:
            street_address += " " + addr.street_address_2
        phone = ""
        try:
            phone = info.find_element_by_css_selector("div.popup-phone").text.strip()
        except:
            pass
        hours_of_operation = info.find_element_by_css_selector(
            "div.popup-hours"
        ).text.strip()
        location_name = info.find_element_by_css_selector("h5.popup-name").text.strip()
        info.find_element_by_css_selector("button.mapboxgl-popup-close-button").click()
        time.sleep(1)
        if "Coming Soon" in hours_of_operation:
            continue
        logger.info(location_name)
        yield SgRecord(
            page_url=base_url,
            location_name=location_name,
            street_address=street_address,
            city=addr.city,
            state=addr.state,
            zip_postal=addr.postcode,
            country_code="US",
            locator_domain=locator_domain,
            phone=phone,
            hours_of_operation=hours_of_operation,
            raw_address=raw_address,
        )

    if driver:
        driver.close()


if __name__ == "__main__":
    with SgWriter(
        SgRecordDeduper(
            SgRecordID({SgRecord.Headers.CITY, SgRecord.Headers.STREET_ADDRESS})
        )
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
