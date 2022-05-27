import time
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgselenium import SgFirefox
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from sglogging import SgLogSetup
from sgpostal.sgpostal import International_Parser, parse_address

logger = SgLogSetup().get_logger("upgas")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.upgas.com"
    base_url = "https://www.upgas.com/locations"
    with SgFirefox() as driver:
        driver.get(base_url)
        time.sleep(10)
        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located(
                (By.XPATH, "//ul[@class='dmGeoMLocList']/li/a")
            )
        )
        links = driver.find_elements_by_xpath("//ul[@class='dmGeoMLocList']/li")
        for link in links:
            logger.info(link.find_element_by_xpath(".//a").text)
            driver.execute_script(
                "arguments[0].click();", link.find_element_by_xpath(".//a")
            )
            block = driver.find_element_by_xpath("//div[@class='dmGeoSingleView']")
            content = block.find_element_by_xpath(
                './/div[@class="dmGeoSVAddr"]'
            ).text.split(",")
            ad = "".join(content)
            a = parse_address(International_Parser(), ad)
            street_address = f"{a.street_address_1} {a.street_address_2}".replace(
                "None", ""
            ).strip()
            if street_address.isdigit() or street_address == "<MISSING>":
                street_address = ad.split(",")[0].strip()
            state = a.state or "<MISSING>"
            zip_postal = a.postcode or "<MISSING>"
            country_code = "US"
            city = a.city or "<MISSING>"
            phone = content[-1]
            location_name = block.find_element_by_xpath(
                './/div[@class="dmGeoSVTitle"]'
            ).text

            row = SgRecord(
                locator_domain=locator_domain,
                page_url=base_url,
                location_name=location_name,
                street_address=street_address,
                city=city,
                state=state,
                zip_postal=zip_postal,
                country_code=country_code,
                store_number=SgRecord.MISSING,
                phone=phone,
                location_type=SgRecord.MISSING,
                latitude=SgRecord.MISSING,
                longitude=SgRecord.MISSING,
                hours_of_operation=SgRecord.MISSING,
                raw_address=ad,
            )

            sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.STREET_ADDRESS}))
    ) as writer:
        fetch_data(writer)
