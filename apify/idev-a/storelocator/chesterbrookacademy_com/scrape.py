from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgselenium import SgChrome
import ssl
from bs4 import BeautifulSoup as bs
import json
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


_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.chesterbrookacademy.com"
json_url = "https://www.chesterbrookacademy.com/wp-admin/admin-ajax.php"
base_url = "https://www.chesterbrookacademy.com/schools-by-state/"


def fetch_data():
    with SgChrome() as driver:
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


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
