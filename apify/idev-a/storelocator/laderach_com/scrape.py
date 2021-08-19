from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from bs4 import BeautifulSoup as bs
from sglogging import SgLogSetup
from sgselenium import SgChrome
from sgrequests import SgRequests
from sgscrape.sgpostal import parse_address_intl
import json
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


def _time(val):
    val = str(val)
    if len(val) == 3:
        val = "0" + val
    return val[:2] + ":" + val[2:]


locator_domain = "https://laderach.com/"
base_url = "https://us.laderach.com/our-locations/"


def fetch_data():
    with SgRequests() as session:
        with SgChrome() as driver:
            driver.get(base_url)
            soup = bs(driver.page_source, "lxml")
            stores = soup.select("div.store-row-container div.store-row")
            logger.info(f"{len(stores)} found")
            for store in stores:
                driver.get(store.iframe["src"])
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located(
                        (
                            By.XPATH,
                            '//div[@class="sk-google-business-profile-container"]',
                        )
                    )
                )
                sp1 = bs(driver.page_source, "lxml")
                if sp1.select_one(".sk-google-business-profile-coming-soon-text"):
                    continue
                url = f"https://data.accentapi.com/feed/{store.iframe['src'].split('/')[-1]}.json?nocache=1622049836522"
                logger.info(url)
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
                if country_code == "United Arab Emirates":
                    street_address = " ".join(_addr.split("-")[:-3])
                    city = _addr.split("-")[-3]
                    state = _addr.split("-")[-2]
                    zip_postal = ""
                hours = []
                if _["content"]["open_hours"]:
                    for hh in json.loads(_["content"]["open_hours"]):
                        if not hh["time_end"]:
                            continue
                        hours.append(
                            f"{hh['day']} {_time(hh['time_start'])}-{_time(hh['time_end'])}"
                        )
                yield SgRecord(
                    page_url=_["content"]["website"],
                    location_name=_["content"]["place_name"],
                    store_number=store["id"].split("-")[-1],
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
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
