from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgselenium import SgChrome
from bs4 import BeautifulSoup as bs
from sglogging import SgLogSetup
from sgscrape.sgpostal import parse_address_intl
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
import ssl

try:
    _create_unverified_https_context = (
        ssl._create_unverified_context
    )  # Legacy Python that doesn't verify HTTPS certificates by default
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context  # Handle target environment that doesn't support HTTPS verification


logger = SgLogSetup().get_logger("dunkindonuts")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.dunkindonuts.co.nz"
base_url = "https://www.dunkindonuts.co.nz/locations"


def fetch_data():
    with SgChrome() as driver:
        driver.get(base_url)
        links = driver.find_elements_by_css_selector("div#Containercf5y a")
        logger.info(f"{len(links)} found")
        for link in links:
            logger.info(link.text)
            blocks = []
            while True:
                driver.execute_script("arguments[0].click();", link)
                try:
                    WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located(
                            (By.XPATH, "//div[@id='POPUPS_ROOT']")
                        )
                    )
                    blocks = driver.find_elements_by_css_selector(
                        'div#POPUPS_ROOT div[data-testid="mesh-container-content"] div[data-testid="richTextElement"]'
                    )
                except:
                    pass
                if blocks:
                    break
            addr = None
            street_address = phone = ""
            for block in blocks:
                _addr = None
                _ps = block.find_elements_by_xpath(".//p")
                if _ps:
                    if len(_ps) > 2:
                        _addr = block.find_element_by_xpath(".//p").text
                    else:
                        _addr = " ".join(
                            [
                                aa.text.strip()
                                for aa in block.find_elements_by_xpath(".//h6")
                            ]
                        )
                    addr = parse_address_intl(_addr.split("(")[0])
                    street_address = addr.street_address_1
                    if addr.street_address_2:
                        street_address += " " + addr.street_address_2
                    phone = _ps[-1].text.replace("Phone", "").strip()
                    break

            hours = []
            sp1 = bs(driver.page_source, "lxml")
            for hh in sp1.select(
                'div#POPUPS_ROOT div[data-testid="mesh-container-content"] div[data-testid="richTextElement"]'
            )[-1].findChildren(recursive=False):
                _hr = hh.text.replace("\xa0", "").strip()
                if "hours" in _hr.lower():
                    break
                if not _hr:
                    continue
                hours.append(_hr)
            yield SgRecord(
                page_url=base_url,
                location_name=blocks[0].text.replace("\n", "").strip(),
                street_address=street_address,
                city=addr.city,
                state=addr.state,
                zip_postal=addr.postcode,
                country_code="New Zealand",
                phone=phone,
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours).replace("–", "-"),
            )


if __name__ == "__main__":
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {
                    SgRecord.Headers.LOCATION_NAME,
                    SgRecord.Headers.STREET_ADDRESS,
                    SgRecord.Headers.ZIP,
                    SgRecord.Headers.PHONE,
                }
            )
        )
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
