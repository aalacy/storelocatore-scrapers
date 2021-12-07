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
from tenacity import retry, stop_after_attempt

try:
    _create_unverified_https_context = (
        ssl._create_unverified_context
    )  # Legacy Python that doesn't verify HTTPS certificates by default
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context  # Handle target environment that doesn't support HTTPS verification

logger = SgLogSetup().get_logger("amplifonusa")

locator_domain = "https://www.amplifonusa.com"
base_url = "https://www.amplifonusa.com/our-program/clinic-locator/search-results-page?addr=&lat={}&long={}"
json_url = "https://www.amplifonusa.com/our-program/clinic-locator/search-results-page.ahhcgetStores.json"


def get_driver():
    return SgChrome(
        executable_path=ChromeDriverManager().install(),
        user_agent="Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:78.0) Gecko/20100101 Firefox/78.0",
        is_headless=True,
    ).driver()


@retry(stop=stop_after_attempt(3))
def get_url(driver=None, url=None):
    if not driver:
        driver = get_driver()
    try:
        driver.get(url)
        driver.wait_for_request(json_url, timeout=20)
    except:
        time.sleep(1)
        logger.info(f"retry {url}")
        driver = None


def fetch_data(search):
    driver = get_driver()
    for lat, lng in search:
        del driver.requests
        get_url(driver, base_url.format(lat, lng))
        locations = bs(driver.page_source, "lxml").select("li.sl-result-list__item")
        logger.info(f"[{lat, lng}] {len(locations)}")
        if locations:
            search.found_location_at(lat, lng)
        for _ in locations:
            if not _.text.strip():
                continue
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


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.GeoSpatialId)) as writer:
        search = DynamicGeoSearch(country_codes=[SearchableCountries.USA])
        results = fetch_data(search)
        for rec in results:
            writer.write_row(rec)
