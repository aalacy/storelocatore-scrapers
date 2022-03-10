from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgselenium import SgChrome
import ssl
from bs4 import BeautifulSoup as bs
import json
from webdriver_manager.chrome import ChromeDriverManager
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("")

try:
    _create_unverified_https_context = (
        ssl._create_unverified_context
    )  # Legacy Python that doesn't verify HTTPS certificates by default
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context  # Handle target environment that doesn't support HTTPS verification

locator_domain = "https://www.chesterbrookacademy.com"
json_url = "https://www.chesterbrookacademy.com/wp-admin/admin-ajax.php"
base_url = "https://www.chesterbrookacademy.com/schools-by-state/"


def get_driver():
    return SgChrome(
        executable_path=ChromeDriverManager().install(),
        user_agent="Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:78.0) Gecko/20100101 Firefox/78.0",
        is_headless=True,
    ).driver()


def fetch_data():
    driver = get_driver()
    driver.get(base_url)
    states = bs(driver.page_source, "lxml").select("ul#nobel_state_list a")
    for state in states:
        state_url = state["href"]
        logger.info(state_url)
        del driver.requests
        driver.get(state_url)
        rr = driver.wait_for_request(json_url)
        locations = json.loads(rr.response.body)["data"]
        for _ in locations:
            yield SgRecord(
                page_url=_["url"],
                location_name=_["name"],
                street_address=_["address"],
                city=_["city"],
                state=_["state"],
                zip_postal=_["zip"],
                latitude=_["lat"],
                longitude=_["lng"],
                country_code="US",
                phone=_["phone"],
                locator_domain=locator_domain,
            )

    if driver:
        driver.close()


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.GeoSpatialId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
