from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sglogging import SgLogSetup
from sgselenium import SgChrome
from sgzip.dynamic import DynamicZipSearch, SearchableCountries
from webdriver_manager.chrome import ChromeDriverManager
import dirtyjson as json
from bs4 import BeautifulSoup as bs
import ssl

try:
    _create_unverified_https_context = (
        ssl._create_unverified_context
    )  # Legacy Python that doesn't verify HTTPS certificates by default
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context  # Handle target environment that doesn't support HTTPS verification

logger = SgLogSetup().get_logger("mitre10")

locator_domain = "https://www.mitre10.co.nz"
base_url = "https://www.mitre10.co.nz/store-locator"
json_url = "https://www.mitre10.co.nz/store-locator"


def get_driver():
    return SgChrome(
        executable_path=ChromeDriverManager().install(),
        user_agent="Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:78.0) Gecko/20100101 Firefox/78.0",
        is_headless=True,
    ).driver()


def fetch_records(search):
    driver = get_driver()
    for zip in search:
        url = f"{base_url}?q={zip}&page=0&type=data"
        driver.get(url)
        try:
            locations = json.loads(bs(driver.page_source, "lxml").text)["data"]
        except:
            continue

        logger.info(f"[{search.current_country()}] [{zip}] {len(locations)}")
        for _ in locations:
            street_address = _["line1"]
            if _["line2"]:
                street_address += " " + _["line2"]
            hours = []
            for day, hh in _["openings"].items():
                hours.append(f"{day}: {hh}")
            page_url = f"{base_url}?branchId={_['storeCode']}&storeName={_['sanitisedDisplayName']}"
            yield SgRecord(
                page_url=page_url,
                location_name=_["displayName"],
                store_number=_["storeCode"],
                street_address=street_address,
                city=_["town"],
                state=_["country"],
                zip_postal=_["postalCode"],
                country_code=_["country"],
                phone=_["phone"],
                latitude=_["latitude"],
                longitude=_["longitude"],
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours),
            )

    if driver:
        driver.close()


if __name__ == "__main__":
    search = DynamicZipSearch(
        country_codes=[SearchableCountries.NEW_ZEALAND], expected_search_radius_miles=10
    )
    with SgWriter(
        deduper=SgRecordDeduper(
            RecommendedRecordIds.StoreNumberId, duplicate_streak_failure_factor=10
        )
    ) as writer:
        for rec in fetch_records(search):
            writer.write_row(rec)
