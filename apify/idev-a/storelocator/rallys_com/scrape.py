from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from bs4 import BeautifulSoup as bs
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.rallys.com/"
start_url = "https://locations.rallys.com/index.html"
base_url = "https://liveapi.yext.com/v2/accounts/me/answers/vertical/query?experienceKey=checkers_answers&api_key=3a0695216a74763b09659ee6021687a0&v=20190101&version=PRODUCTION&locale=en&input={}&verticalKey=restaurants&limit=50&offset={}&facetFilters=%7B%7D&session_id=0396ea7e-3878-4d7d-9e94-0a1b61f30d1f&sessionTrackingEnabled=true&sortBys=%5B%5D&referrerPageUrl=https%3A%2F%2Flocations.rallys.com%2F&source=STANDARD&jsLibVersion=v1.11.0"

days = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]


def fetch_data():
    with SgRequests() as session:
        states = bs(session.get(start_url, headers=_headers).text, "lxml").select(
            "div.Main-content span.Directory-listLinkText"
        )
        for state in states:
            offset = 0
            while True:
                st = state.text.strip()
                locations = session.get(
                    base_url.format(st, offset), headers=_headers
                ).json()["response"]["results"]
                cnt = len(locations)
                logger.info(f"[{st}] [{offset}] {cnt} found")
                offset += cnt
                if not cnt:
                    break

                for loc in locations:
                    _ = loc["data"]
                    addr = _["address"]
                    hours = []
                    for day, hh in _.get("hours", {}).items():
                        if day not in days:
                            break
                        times = []
                        for hr in hh.get("openIntervals", []):
                            times.append(f"{hr['start']} - {hr['end']}")
                        hours.append(f"{day}: {' '.join(times)}")
                    yield SgRecord(
                        page_url=_["website"],
                        store_number=_["id"],
                        location_name=_["name"],
                        street_address=addr["line1"],
                        city=addr["city"],
                        state=addr["region"],
                        zip_postal=addr["postalCode"],
                        latitude=_["yextDisplayCoordinate"]["latitude"],
                        longitude=_["yextDisplayCoordinate"]["longitude"],
                        country_code=addr["countryCode"],
                        phone=_["mainPhone"],
                        location_type=_["type"],
                        locator_domain=locator_domain,
                        hours_of_operation="; ".join(hours),
                    )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
