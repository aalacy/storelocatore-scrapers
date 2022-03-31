from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgselenium import SgChrome
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from sglogging import SgLogSetup
import time
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

logger = SgLogSetup().get_logger("parkersga")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


days = {
    "Dimanche": "Sun",
    "Jeudi": "Thu",
    "Lundi": "Mon",
    "Mercredi": "Wed",
    "Samedi": "Sat",
    "Vendredi": "Fri",
    "Mardi": "Tue",
}


def fetch_data():
    locator_domain = "https://www.parkersga.com/"
    base_url = "https://www.parkersga.com/stores"
    with SgChrome() as driver:
        driver.get(base_url)
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(
                (By.XPATH, "//ul[@class='dmGeoMLocList']/li/a")
            )
        )
        links = driver.find_elements_by_xpath("//ul[@class='dmGeoMLocList']/li")
        for link in links:
            logger.info(link.find_element_by_xpath(".//a").text)
            block = None
            while True:
                driver.execute_script(
                    "arguments[0].click();", link.find_element_by_xpath(".//a")
                )
                time.sleep(1)
                block = driver.find_element_by_xpath("//div[@class='dmGeoSingleView']")
                if block.text.strip():
                    break
            raw_address = block.find_element_by_xpath(
                './/div[@class="dmGeoSVAddr"]'
            ).text
            content = raw_address.split(",")
            zip_postal = content[2]
            state = content[-3]
            if not zip_postal.strip().isdigit():
                zip_postal = ""
            if content[3].strip().isdigit():
                zip_postal = content[3]
                state = content[2]
            yield SgRecord(
                page_url=base_url,
                store_number=link.get_attribute("geoid"),
                location_name=block.find_element_by_xpath(
                    './/div[@class="dmGeoSVTitle"]'
                ).text,
                street_address=content[0],
                city=content[1],
                zip_postal=zip_postal,
                state=state,
                country_code=content[-2],
                phone=content[-1],
                locator_domain=locator_domain,
                raw_address=raw_address,
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
