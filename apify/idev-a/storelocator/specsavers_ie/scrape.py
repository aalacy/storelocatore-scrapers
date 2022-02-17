from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgselenium import SgChrome
from bs4 import BeautifulSoup as bs
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sglogging import SgLogSetup
import ssl

try:
    _create_unverified_https_context = (
        ssl._create_unverified_context
    )  # Legacy Python that doesn't verify HTTPS certificates by default
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context  # Handle target environment that doesn't support HTTPS verification

logger = SgLogSetup().get_logger("specsavers")

_headers = {
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "accept-language": "en-US,en;q=0.9",
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.specsavers.ie"
base_url = "https://www.specsavers.ie/stores/full-store-list"


def fetch_data():
    with SgChrome(
        user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1"
    ) as driver:
        with SgRequests() as session:
            driver.get(base_url)
            cookies = []
            for cookie in driver.get_cookies():
                cookies.append(f"{cookie['name']}={cookie['value']}")
            _headers["cookie"] = "; ".join(cookies)
            soup = bs(driver.page_source, "lxml")
            locations = soup.select("div.item-list ul a")
            for link in locations:
                page_url = "https://www.specsavers.ie/stores/" + link["href"]
                logger.info(page_url)
                sp1 = bs(session.get(page_url, headers=_headers).text, "lxml")
                raw_address = " ".join(sp1.select_one("div.store p").stripped_strings)
                json_url = sp1.select_one("div.js-yext-info")["data-yext-url"]
                _ = session.get(json_url, headers=_headers).json()["response"]
                hours = [
                    ": ".join(hh.stripped_strings)
                    for hh in sp1.select("table.opening--day-and-time tr")
                ]
                if _.get("displayLat"):
                    latitude = _["displayLat"]
                    longitude = _["displayLng"]
                elif _.get("yextDisplayLat"):
                    latitude = _["yextDisplayLat"]
                    longitude = _["yextDisplayLng"]
                yield SgRecord(
                    page_url=page_url,
                    location_name=sp1.h1.text.strip(),
                    street_address=_["address"],
                    city=_["city"],
                    state=_.get("state"),
                    zip_postal=_.get("zip"),
                    country_code=_["countryCode"],
                    phone=_["phone"],
                    latitude=latitude,
                    longitude=longitude,
                    locator_domain=locator_domain,
                    hours_of_operation="; ".join(hours),
                    raw_address=raw_address.replace("\n", ""),
                )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
