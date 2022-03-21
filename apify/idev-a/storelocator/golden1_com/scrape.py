from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgselenium import SgChrome
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
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
data = "golden1branches=true&golden1homecenters=false&golden1atm=true&sharedbranches=false&sharedatm=false&swlat={}&swlng={}&nelat={}&nelng={}&centerlat={}&centerlng={}&userlat=&userlng="


def fetch_records(search):
    for lat, lng in search:
        with SgRequests(proxy_country="us") as http:
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
                logger.info(f"[{lat}, {lng}] failed")
            logger.info(f"[{lat}, {lng}] {len(locations)} found")
            if locations:
                search.found_location_at(lat, lng)
            for _ in locations:
                if not _["address"] and not _["title"]:
                    continue
                location_type = _["imageUrl"].split("/")[-1].split(".")[0]
                if location_type not in ["golden-1-atm", "golden-1-branch"]:
                    continue
                hours = []
                for hh in _["hours"].split("\\n"):
                    if not hh.strip():
                        continue
                    if "Hour" in hh:
                        continue
                    hours.append(hh.strip())
                hours_of_operation = "; ".join(hours)
                if "Temporarily-Closed" in hours_of_operation:
                    hours_of_operation = "Temporarily-Closed"
                yield SgRecord(
                    page_url="https://www.golden1.com/atm-branch-finder#",
                    location_name=". ".join(_["title"].split(".")[1:]),
                    street_address=_["address"],
                    city=_["city"],
                    state=_["state"],
                    zip_postal=bs(_["zip"], "lxml").text.strip(),
                    latitude=_["lat"],
                    longitude=_["lng"],
                    country_code="US",
                    location_type=location_type,
                    locator_domain=locator_domain,
                    hours_of_operation=hours_of_operation,
                )


if __name__ == "__main__":
    with SgChrome() as driver:
        driver.get(base_link)
        cookies = []
        for cook in driver.get_cookies():
            cookies.append(f'{cook["name"]}={cook["value"]}')
        _headers["cookie"] = ";".join(cookies)
        search = DynamicGeoSearch(
            country_codes=[SearchableCountries.USA], granularity=Grain_8()
        )
        with SgWriter(
            deduper=SgRecordDeduper(
                SgRecordID(
                    {
                        SgRecord.Headers.STREET_ADDRESS,
                        SgRecord.Headers.CITY,
                        SgRecord.Headers.STATE,
                    }
                ),
                duplicate_streak_failure_factor=1000,
            )
        ) as writer:
            for rec in fetch_records(search):
                writer.write_row(rec)
