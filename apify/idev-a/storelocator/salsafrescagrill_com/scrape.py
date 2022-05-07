from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgselenium import SgFirefox
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from sglogging import SgLogSetup
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
import time
from sgpostal.sgpostal import parse_address_intl

logger = SgLogSetup().get_logger("salsafrescagrill")
map_url = r"api\.maptiler\.com/tiles/v3"
locator_domain = "https://www.salsafrescagrill.com/"
base_url = "https://www.salsafrescagrill.com/locations"


def fetch_data():
    with SgFirefox(block_third_parties=True) as driver:
        driver.get(base_url)
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.XPATH, "//iframe"))
        )
        time.sleep(10)
        iframe = driver.find_element(By.XPATH, "//iframe")
        driver.switch_to.frame(iframe)
        driver.find_element(
            By.CSS_SELECTOR,
            "button.maplibregl-ctrl-fullscreen.mapboxgl-ctrl-fullscreen",
        ).click()
        time.sleep(2)
        for marker in driver.find_elements(
            By.CSS_SELECTOR, 'div[aria-label="Map marker"]'
        ):
            driver.execute_script("arguments[0].click();", marker)
            time.sleep(1)
            info = driver.find_element(By.CSS_SELECTOR, "div.mapboxgl-popup-content")
            raw_address = info.find_element(
                By.CSS_SELECTOR, "p.popup-address"
            ).text.strip()
            addr = parse_address_intl(raw_address)
            street_address = addr.street_address_1
            if addr.street_address_2:
                street_address += " " + addr.street_address_2
            phone = ""
            try:
                phone = info.find_element(
                    By.CSS_SELECTOR, "div.popup-phone"
                ).text.strip()
            except:
                pass
            hours_of_operation = info.find_element(
                By.CSS_SELECTOR, "div.popup-hours"
            ).text.strip()
            location_name = info.find_element(
                By.CSS_SELECTOR, "h5.popup-name"
            ).text.strip()
            info.find_element(
                By.CSS_SELECTOR, "button.mapboxgl-popup-close-button"
            ).click()
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


if __name__ == "__main__":
    with SgWriter(
        SgRecordDeduper(
            SgRecordID({SgRecord.Headers.CITY, SgRecord.Headers.STREET_ADDRESS})
        )
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
