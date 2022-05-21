from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from bs4 import BeautifulSoup as bs
from sgzip.dynamic import DynamicGeoSearch, SearchableCountries
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("carrefour")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.carrefour.es"
base_url = "https://www.carrefour.es/tiendas-carrefour/buscador-de-tiendas/locations.aspx?origLat={}&origLng={}"


def fetch_data(search):
    with SgRequests() as session:
        for lat, lng in search:
            locations = bs(
                session.get(base_url.format(lat, lng), headers=_headers).text, "lxml"
            ).select("marker")
            if locations:
                search.found_location_at(lat, lng)
            logger.info(f"[{lat, lng}] {len(locations)}")
            for _ in locations:
                street_address = _["address"]
                if _.get("address2"):
                    street_address += " " + _["address2"]
                hours = ""
                if _["hours1"]:
                    if "apertura" not in _["hours1"].lower():
                        hours = f"L - S: {_['hours1'].split('24/12')[0]}"
                if not hours and _["hours2"]:
                    if "apertura" not in _["hours2"].lower():
                        hours = f"L - S: {_['hours2']}"
                page_url = _["web"]
                if not page_url.startswith("http"):
                    page_url = locator_domain + page_url
                yield SgRecord(
                    page_url=page_url,
                    location_name=_["name"],
                    street_address=street_address,
                    city=_["city"],
                    state=_["state"],
                    zip_postal=_["postal"],
                    latitude=_["lat"],
                    longitude=_["lng"],
                    country_code="Spain",
                    phone=_["phone"],
                    location_type=_["category"],
                    locator_domain=locator_domain,
                    hours_of_operation=hours.replace(",", ""),
                )


if __name__ == "__main__":
    search = DynamicGeoSearch(
        country_codes=[SearchableCountries.SPAIN], expected_search_radius_miles=500
    )
    with SgWriter(
        SgRecordDeduper(
            RecommendedRecordIds.PageUrlId, duplicate_streak_failure_factor=100
        )
    ) as writer:
        results = fetch_data(search)
        for rec in results:
            writer.write_row(rec)
