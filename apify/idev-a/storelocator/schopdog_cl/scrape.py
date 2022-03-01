from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgselenium import SgChrome
from bs4 import BeautifulSoup as bs
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from sgpostal.sgpostal import parse_address_intl
import ssl
import time

try:
    _create_unverified_https_context = (
        ssl._create_unverified_context
    )  # Legacy Python that doesn't verify HTTPS certificates by default
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context  # Handle target environment that doesn't support HTTPS verification

locator_domain = "https://www.schopdog.cl"
base_url = "https://www.schopdog.cl/sucursales"


def fetch_data():
    with SgChrome() as driver:
        driver.get(base_url)
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located(
                (
                    By.CSS_SELECTOR,
                    "div.ct-stores",
                )
            )
        )
        time.sleep(10)
        soup = bs(driver.page_source, "lxml")
        locations = soup.select("div.ct-stores div.col-xs-12.col-sm-6.col-md-3")
        for loc in locations:
            info = (
                loc.findChildren("div", recursive=False)[0]
                .findChildren("div", recursive=False)[0]
                .findChildren("div", recursive=False)
            )
            raw_address = list(info[1].stripped_strings)[0]
            _addr = raw_address.split()
            zip_postal = ""
            if _addr[-1].strip().isdigit():
                zip_postal = _addr[-1]
                raw_address = " ".join(_addr[:-1])
            addr = parse_address_intl(raw_address)
            street_address = addr.street_address_1
            if addr.street_address_2:
                street_address += " " + addr.street_address_2
            if not street_address:
                street_address = raw_address
            yield SgRecord(
                page_url=base_url,
                location_name=info[0].text.strip(),
                street_address=street_address,
                city=addr.city,
                state=addr.state,
                zip_postal=zip_postal,
                country_code="Chile",
                locator_domain=locator_domain,
                raw_address=list(info[1].stripped_strings)[0],
            )


if __name__ == "__main__":
    with SgWriter(
        SgRecordDeduper(
            SgRecordID({SgRecord.Headers.RAW_ADDRESS, SgRecord.Headers.LOCATION_NAME})
        )
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
