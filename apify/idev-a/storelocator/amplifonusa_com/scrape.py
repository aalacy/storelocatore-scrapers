from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgselenium import SgChrome
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from webdriver_manager.chrome import ChromeDriverManager
from sglogging import SgLogSetup
import time
from bs4 import BeautifulSoup as bs
from sgzip.dynamic import DynamicGeoSearch, SearchableCountries
import ssl

try:
    _create_unverified_https_context = (
        ssl._create_unverified_context
    )  # Legacy Python that doesn't verify HTTPS certificates by default
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context  # Handle target environment that doesn't support HTTPS verification
    
logger = SgLogSetup().get_logger("amplifonusa")

_headers = {
    "accept": "application/json, text/javascript, */*; q=0.01",
    "accept-encoding": "gzip, deflate, br",
    "accept-language": "en-US,en;q=0.9",
    "origin": "https://www.amplifonusa.com",
    "x-requested-with": "XMLHttpRequest",
    "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.amplifonusa.com"
base_url = "https://www.amplifonusa.com/our-program/clinic-locator/search-results-page?addr=&lat={}&long={}"
json_url = "https://www.amplifonusa.com/our-program/clinic-locator/search-results-page.ahhcgetStores.json"


def get_driver():
    return SgChrome(
        executable_path=ChromeDriverManager().install(),
        user_agent="Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:78.0) Gecko/20100101 Firefox/78.0",
        is_headless=True,
    ).driver()


def get_url(driver=None, url=None):
    while True:
        if not driver:
            driver = get_driver()
        try:
            driver.get(url)
            break
        except:
            time.sleep(1)
            logger.info(f"retry {url}")
            driver = None


def fetch_data(search):
    driver = get_driver()
    for lat, lng in search:
        del driver.requests
        get_url(driver, base_url.format(lat, lng))
        driver.wait_for_request(json_url)
        locations = bs(driver.page_source, "lxml").select("li.sl-result-list__item")
        logger.info(f"[{lat, lng}] {len(locations)}")
        if locations:
            search.found_location_at(lat, lng)
        for _ in locations:
            if not _.text.strip():
                continue
            try:
                phone = ""
                if _.select_one("a.phone-number"):
                    phone = _.select_one("a.phone-number").text.strip()
                yield SgRecord(
                    page_url="https://www.amplifonusa.com/our-program/clinic-locator",
                    location_name=_["data-shop-name"],
                    street_address=_["data-shop-address"],
                    city=_["data-shop-city"],
                    state=_["data-shop-state"],
                    zip_postal=_["data-shop-postal-code"],
                    latitude=_["data-shop-latitude"],
                    longitude=_["data-shop-longitude"],
                    country_code="US",
                    phone=phone,
                    locator_domain=locator_domain,
                    raw_address=_.select_one("p.dark-grey-text").text.strip(),
                )
            except:
                import pdb

                pdb.set_trace()


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.GeoSpatialId)) as writer:
        search = DynamicGeoSearch(
            country_codes=[SearchableCountries.USA], expected_search_radius_miles=100
        )
        results = fetch_data(search)
        for rec in results:
            writer.write_row(rec)
