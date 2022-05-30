from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from bs4 import BeautifulSoup as bs
from sgzip.dynamic import DynamicGeoSearch, SearchableCountries
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("com")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://gloriajeanscoffees.com.au/"
base_url = "https://www.gloriajeanscoffees.com.au/wp/wp-admin/admin-ajax.php?action=store_search&lat={}&lng={}&max_results=500&search_radius=500&autoload=1"


def fetch_data(http, search):
    for lat, lng in search:
        locations = http.get(base_url.format(lat, lng), headers=_headers).json()
        if locations:
            search.found_location_at(lat, lng)
        logger.info(f"[{lat, lng}] {len(locations)}")
        for _ in locations:
            street_address = _["address"]
            if _["address2"]:
                street_address += " " + _["address2"]
            hours = []
            if _["hours"]:
                hours = [
                    ": ".join(hh.stripped_strings)
                    for hh in bs(_["hours"], "lxml").select("table tr")
                ]
            state = _["state"]
            zip_postal = _["zip"]
            if state.isdigit() and not zip_postal:
                state = ""
                zip_postal = _["state"]
            yield SgRecord(
                store_number=_["id"],
                location_name=_["store"].replace("&#8217;", "'"),
                street_address=street_address,
                city=_["city"],
                state=state,
                zip_postal=zip_postal,
                latitude=_["lat"],
                longitude=_["lng"],
                country_code=_["country"],
                phone=_["phone"],
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours),
            )


if __name__ == "__main__":
    if __name__ == "__main__":
        with SgRequests() as http:
            search = DynamicGeoSearch(
                country_codes=[SearchableCountries.AUSTRALIA],
                expected_search_radius_miles=500,
            )
            with SgWriter(
                SgRecordDeduper(
                    RecommendedRecordIds.StoreNumberId,
                    duplicate_streak_failure_factor=100,
                )
            ) as writer:
                results = fetch_data(http, search)
                for rec in results:
                    writer.write_row(rec)
