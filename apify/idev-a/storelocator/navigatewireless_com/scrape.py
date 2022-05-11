from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgselenium import SgChrome
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sglogging import SgLogSetup
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
import dirtyjson as json
import ssl

try:
    _create_unverified_https_context = (
        ssl._create_unverified_context
    )  # Legacy Python that doesn't verify HTTPS certificates by default
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context  # Handle target environment that doesn't support HTTPS verification

logger = SgLogSetup().get_logger("navigatewireless")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.navigatewireless.com"
base_url = "https://stores.uscellular.com/navigate-wireless/find-a-store"
json_url = "currentPageId="


def fetch_data():
    with SgRequests() as session:
        with SgChrome() as driver:
            driver.get(base_url)
            rr = driver.wait_for_request(json_url, timeout=20)
            locations = json.loads(rr.response.body)["locations"]
            for _ in locations:
                page_url = "https://stores.uscellular.com" + _["storeDetailsUrl"]
                logger.info(page_url)
                sp1 = bs(session.get(page_url, headers=_headers).text, "lxml")
                hours = []
                days = sp1.select("div.hours div.day")
                timings = sp1.select("div.hours div.timings")
                for x in range(len(days)):
                    hours.append(f"{days[x].text.strip()}: {timings[x].text.strip()}")
                yield SgRecord(
                    page_url=page_url,
                    store_number=_["locationId"],
                    location_name=_["heading"],
                    street_address=_["streetAddress"],
                    city=_["city"],
                    state=_["state"],
                    zip_postal=_["zipCode"],
                    country_code="US",
                    phone=_["phoneNumber"],
                    locator_domain=locator_domain,
                    latitude=_["latitude"],
                    longitude=_["longitude"],
                    hours_of_operation="; ".join(hours),
                )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
