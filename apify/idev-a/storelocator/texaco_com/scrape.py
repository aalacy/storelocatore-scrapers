from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sglogging import SgLogSetup
from sgrequests.sgrequests import SgRequests
from sgzip.dynamic import DynamicGeoSearch, SearchableCountries

logger = SgLogSetup().get_logger("quizclothing")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.texaco.com"
base_url = "https://apis.chevron.com/api/StationFinder/nearby?clientid=A67B7471&lat={}&lng={}&oLat={}&oLng={}&brand=chevronTexaco&radius=35"


def _c(val):
    return val.replace(" ", "-").replace("#", "").replace(",", "").replace(".", "")


def fetch_records(http, search):
    for lat, lng in search:
        locations = http.get(
            base_url.format(lat, lng, lat, lng), headers=_headers
        ).json()["stations"]
        if locations:
            search.found_location_at(lat, lng)
        logger.info(f"[{lat, lng}] {len(locations)}")
        for _ in locations:
            street_address = _["address"]
            zip_postal = _["zip"]
            country_code = "US"
            if "C.P." in street_address:
                page_url = "https://www.texaco.com/en_us/home/find-a-station.html"
                zip_postal = (
                    "C.P. " + street_address.split("C.P.")[-1].replace(",", "").strip()
                )
                street_address = street_address.split("C.P.")[0]
                country_code = "Mexico"
            else:
                page_url = f"https://www.texaco.com/en_us/home/find-a-station.html?/station/{_c(street_address)}-{_c(_['city'])}-{_c(_['state'])}--{_c(_['zip'])}-id{_['id']}"
            yield SgRecord(
                page_url=page_url,
                location_name=_["name"],
                store_number=_["id"],
                street_address=street_address,
                city=_["city"],
                state=_["state"],
                zip_postal=zip_postal,
                country_code=country_code,
                phone=_["phone"],
                latitude=_["lat"],
                longitude=_["lng"],
                locator_domain=locator_domain,
                hours_of_operation=_["hours"],
            )


if __name__ == "__main__":
    with SgRequests() as http:
        search = DynamicGeoSearch(
            country_codes=[SearchableCountries.USA], expected_search_radius_miles=20
        )
        with SgWriter(
            SgRecordDeduper(
                RecommendedRecordIds.StoreNumberId, duplicate_streak_failure_factor=100
            )
        ) as writer:
            for rec in fetch_records(http, search):
                writer.write_row(rec)
