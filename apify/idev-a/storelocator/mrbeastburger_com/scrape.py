from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgzip.dynamic import DynamicGeoSearch, SearchableCountries
from sglogging import SgLogSetup
from datetime import datetime, timedelta

logger = SgLogSetup().get_logger("quizclothing")
_headers = {
    "accept": "application/json",
    "content-type": "application/json",
    "x-device-id": "1d605e0d-84ed-493a-98d2-fa501440775f",
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://mrbeastburger.com"
base_url = "https://api.dineengine.io/mrbeastburger/custom/dineengine/vendor/olo/restaurants/near?lat={}&long={}&radius=500&limit=100&calendarstart={}&calendarend={}"


def fetch_data(search):
    today = datetime.today()
    mon = (today + timedelta(days=-today.weekday())).strftime("%Y%m%d")
    next_mon = (today + timedelta(days=-today.weekday(), weeks=1)).strftime("%Y%m%d")
    for lat, lng in search:
        with SgRequests(proxy_country="us") as session:
            locations = session.get(
                base_url.format(lat, lng, mon, next_mon), headers=_headers
            ).json()["restaurants"]
            if locations:
                search.found_location_at(lat, lng)
            logger.info(f"[{lat, lng}] {len(locations)}")
            for _ in locations:
                hours = []
                for hr in _["calendars"]:
                    if not hr["label"]:
                        for hh in hr["ranges"]:
                            hours.append(
                                f"{hh['weekday']}: {hh['start'].split()[-1]} - {hh['end'].split()[-1]}"
                            )
                        break
                yield SgRecord(
                    store_number=_["id"],
                    location_name=_["name"],
                    street_address=_["streetaddress"],
                    city=_["city"],
                    state=_["state"],
                    zip_postal=_["zip"],
                    latitude=_["latitude"],
                    longitude=_["longitude"],
                    country_code=_["country"],
                    phone=_["telephone"],
                    locator_domain=locator_domain,
                    hours_of_operation="; ".join(hours),
                )


if __name__ == "__main__":
    search = DynamicGeoSearch(
        country_codes=[SearchableCountries.USA], expected_search_radius_miles=100
    )
    with SgWriter(
        SgRecordDeduper(
            RecommendedRecordIds.StoreNumberId, duplicate_streak_failure_factor=100
        )
    ) as writer:
        results = fetch_data(search)
        for rec in results:
            writer.write_row(rec)
