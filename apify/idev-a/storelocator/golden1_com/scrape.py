from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgselenium import SgChrome
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from typing import Iterable
from sgzip.dynamic import SearchableCountries, DynamicGeoSearch, Grain_8
from sglogging import SgLogSetup
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


logger = SgLogSetup().get_logger("golden1")

_headers = {
    "accept": "application/json, text/javascript, */*; q=0.01",
    "accept-encoding": "gzip, deflate, br",
    "accept-language": "en-US,en;q=0.9",
    "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
    "origin": "https://www.golden1.com",
    "referer": "https://www.golden1.com/atm-branch-finder",
    "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36",
}

locator_domain = "https://www.golden1.com"
base_link = "https://www.golden1.com/atm-branch-finder"
base_url = "https://www.golden1.com/api/BranchLocator/GetLocations"
data = "golden1branches=true&golden1homecenters=false&golden1atm=false&sharedbranches=true&sharedatm=false&swlat=&swlng=&nelat=&nelng=&centerlat={}&centerlng={}&userlat=&userlng="


def fetch_records(http: SgRequests, search: DynamicGeoSearch) -> Iterable[SgRecord]:
    for lat, lng in search:
        locations = http.post(
            base_url, headers=_headers, data=data.format(lat, lng)
        ).json()["locations"]
        logger.info(f"[{lat}, {lng}] {len(locations)} found")
        for _ in locations:
            yield SgRecord(
                page_url="https://www.golden1.com/atm-branch-finder#",
                location_name=_["title"],
                street_address=_["address"],
                city=_["city"],
                state=_["state"],
                zip_postal=bs(_["zip"], "lxml").text.strip(),
                latitude=_["lat"],
                longitude=_["lng"],
                country_code="US",
                locator_domain=locator_domain,
                hours_of_operation=_["hours"].replace("\\n", "; "),
            )


if __name__ == "__main__":
    with SgChrome() as driver:
        driver.get(base_link)
        cookies = driver.get_cookies()
        cookie = ""
        for cook in cookies:
            cookie = cookie + cook["name"] + "=" + cook["value"] + "; "

        _headers["cookie"] = cookie.strip()[:-1]
        search = DynamicGeoSearch(
            country_codes=[SearchableCountries.USA], granularity=Grain_8()
        )
        with SgWriter(
            deduper=SgRecordDeduper(RecommendedRecordIds.GeoSpatialId)
        ) as writer:
            with SgRequests(proxy_country="us") as http:
                for rec in fetch_records(http, search):
                    writer.write_row(rec)
