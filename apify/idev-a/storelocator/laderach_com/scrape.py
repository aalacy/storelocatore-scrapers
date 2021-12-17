from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from bs4 import BeautifulSoup as bs
from sglogging import SgLogSetup
from sgselenium import SgChrome
from sgrequests import SgRequests
from sgscrape.sgpostal import parse_address_intl
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By

import ssl

try:
    _create_unverified_https_context = (
        ssl._create_unverified_context
    )  # Legacy Python that doesn't verify HTTPS certificates by default
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context  # Handle target environment that doesn't support HTTPS verification

logger = SgLogSetup().get_logger("laderach")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://laderach.com/"
base_url = "https://us.laderach.com/our-locations/"


def fetch_data(session):
    with SgChrome() as driver:
        driver.get(base_url)
        soup = bs(driver.page_source, "lxml")
        stores = soup.select("div.store-row-container div.store-row")
        logger.info(f"{len(stores)} found")
        for store in stores:
            store_number = store.iframe["src"].split("/")[-1]
            logger.info(store_number)
            if store_number == "50047" or store_number == "63198":
                continue
            driver.get(store.iframe["src"])
            try:
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located(
                        (
                            By.XPATH,
                            '//div[@class="sk-google-business-profile-container"]',
                        )
                    )
                )
            except:
                continue
            sp1 = bs(driver.page_source, "lxml")
            if sp1.select_one(".sk-google-business-profile-coming-soon-text"):
                continue
            url = f"https://data.accentapi.com/feed/{store_number}.json?nocache=1622049836522"
            _ = session.get(url, headers=_headers).json()
            _addr = _["content"]["location"]
            addr = parse_address_intl(_addr)
            city = addr.city
            state = addr.state
            zip_postal = addr.postcode
            street_address = addr.street_address_1
            if addr.street_address_2:
                street_address += " " + addr.street_address_2
            if street_address.isdigit() and len(_addr.split(",")) > 1:
                street_address = _addr.split(",")[0]
            country_code = addr.country
            if not country_code and "Singapore" in _addr:
                country_code = "Singapore"
            hours = _["content"].get("week_day_text", [])
            yield SgRecord(
                page_url=_["content"]["website"],
                location_name=_["content"]["place_name"],
                store_number=store_number,
                street_address=street_address,
                city=city,
                state=state,
                zip_postal=zip_postal,
                country_code=country_code,
                phone=_["content"]["phone"],
                locator_domain=locator_domain,
                location_type=_["content"]["place_type"],
                hours_of_operation="; ".join(hours),
                latitude=sp1.select_one(".place_lat").text,
                longitude=sp1.select_one(".place_lng").text,
                raw_address=_["content"]["location"],
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        with SgRequests() as session:
            results = fetch_data(session)
            for rec in results:
                writer.write_row(rec)
