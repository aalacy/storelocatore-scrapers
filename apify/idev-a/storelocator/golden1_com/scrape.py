from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgselenium import SgChrome
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from typing import Iterable
from sgzip.dynamic import SearchableCountries, DynamicGeoSearch
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
data = "golden1branches=true&golden1homecenters=false&golden1atm=true&sharedbranches=false&sharedatm=false&swlat={}&swlng={}&nelat={}&nelng={}&centerlat={}&centerlng={}&userlat=&userlng="


def fetch_records(http: SgRequests, search: DynamicGeoSearch) -> Iterable[SgRecord]:
    for lat, lng in search:
        swlat = lat - 0.207706338
        swlng = lng - 0.26463210582
        nelat = lat + 0.207706338
        netlng = lng + 0.26463210582
        try:
            locations = http.post(
                base_url,
                headers=_headers,
                data=data.format(swlat, swlng, nelat, netlng, lat, lng),
            ).json()["locations"]
        except:
            locations = []
        logger.info(f"[{lat}, {lng}] {len(locations)} found")
        search.found_location_at(lat, lng)
        for _ in locations:
            if not _["address"] and not _["title"]:
                continue
            location_type = ""
            if "branch" in _["imageUrl"]:
                location_type = "branch"
            if "atm" in _["imageUrl"]:
                location_type = "atm"
            hours = []
            for hh in _["hours"].split("\\n"):
                if not hh.strip():
                    continue
                if "Hour" in hh:
                    continue
                hours.append(hh.strip())
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
                location_type=location_type,
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours),
            )


if __name__ == "__main__":
    with SgChrome() as driver:
        driver.get(base_link)
        cookies = []
        for cook in driver.get_cookies():
            cookies.append(f'{cook["name"]}={cook["value"]}')
        _headers["cookie"] = ";".join(cookies)
        search = DynamicGeoSearch(
            country_codes=[SearchableCountries.USA], expected_search_radius_miles=500
        )
        with SgWriter(
            deduper=SgRecordDeduper(
                RecommendedRecordIds.GeoSpatialId, duplicate_streak_failure_factor=1000
            )
        ) as writer:
            with SgRequests(proxy_country="us") as http:
                for rec in fetch_records(http, search):
                    writer.write_row(rec)
