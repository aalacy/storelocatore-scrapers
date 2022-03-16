from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgselenium import SgChrome
from bs4 import BeautifulSoup as bs
from sgpostal.sgpostal import parse_address_intl
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
import ssl
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By

try:
    _create_unverified_https_context = (
        ssl._create_unverified_context
    )  # Legacy Python that doesn't verify HTTPS certificates by default
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context  # Handle target environment that doesn't support HTTPS verification

locator_domain = "https://www.chickncone.com/"
base_url = "https://chickncone.com/locations/"


def fetch_data():
    with SgChrome(
        user_agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.54 Safari/537.36"
    ) as driver:
        driver.get(base_url)
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(
                (
                    By.CSS_SELECTOR,
                    "div.item",
                )
            )
        )
        locations = bs(driver.page_source, "lxml").select("div.item")
        for _ in locations:
            raw_address = (
                _.select_one("div.content div")
                .text.strip()
                .replace("UAE", "United Arab Emirates")
            )
            addr = parse_address_intl(raw_address)
            street_address = addr.street_address_1
            if addr.street_address_2:
                street_address += " " + addr.street_address_2
            country_code = addr.country or "US"
            if addr.city and addr.city == "Sharjah":
                country_code = "UAE"
            coord = (
                _.select_one("a.direction")["href"]
                .split("&destination=")[1]
                .strip()
                .split(",")
            )

            yield SgRecord(
                page_url=base_url,
                location_name=_.select_one("a.title").text.strip(),
                street_address=addr.street_address_1,
                city=addr.city,
                state=addr.state,
                zip_postal=addr.postcode,
                country_code=country_code,
                latitude=coord[0],
                longitude=coord[1],
                locator_domain=locator_domain,
                raw_address=raw_address,
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.GeoSpatialId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
