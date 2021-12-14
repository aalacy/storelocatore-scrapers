from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgzip.dynamic import DynamicGeoSearch, SearchableCountries
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("quizclothing")
_headers = {
    "accept": "application/json",
    "content-type": "application/json",
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://mrbeastburger.com"
base_url = "https://api.dineengine.io/mrbeastburger/custom/dineengine/vendor/olo/restaurants/near?lat={}&long={}&radius=500&limit=100&calendarstart=20211206&calendarend=20211213"


def fetch_data(search):
    for lat, lng in search:
        with SgRequests() as session:
            locations = session.get(base_url.format(lat, lng), headers=_headers).json()[
                "restaurants"
            ]
            if locations:
                search.found_location_at(lat, lng)
            logger.info(f"[{lat, lng}] {len(locations)}")
            for _ in locations:
                yield SgRecord(
                    page_url=base_url,
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
