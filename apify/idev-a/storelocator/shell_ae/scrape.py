from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sglogging import SgLogSetup
from sgzip.dynamic import DynamicGeoSearch, SearchableCountries

logger = SgLogSetup().get_logger("shell")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.shell.ae/"
json_url = "https://shelllubricantslocator.geoapp.me/api/v1/global_lubes/locations/nearest_to?lat={}&lng={}&format=json"


def fetch_data(search):
    with SgRequests() as session:
        for lat, lng in search:
            locations = session.get(json_url.format(lat, lng), headers=_headers).json()
            logger.info(f"[{search.current_country()}] [{lat, lng}] {len(locations)}")
            if locations:
                search.found_location_at(lat, lng)
            for _ in locations:
                street_address = ""
                if _.get("address"):
                    street_address = _["address"]
                if _.get("address1"):
                    street_address += " " + _["address1"]
                if _.get("address2"):
                    street_address += " " + _["address2"]
                zip_postal = _.get("postcode")
                if zip_postal and zip_postal == "00000":
                    zip_postal = ""
                yield SgRecord(
                    page_url="",
                    store_number=_["id"],
                    location_name=_["name"],
                    street_address=street_address,
                    city=_["city"],
                    state=_.get("state"),
                    zip_postal=zip_postal,
                    latitude=_["lat"],
                    longitude=_["lng"],
                    country_code=_["country"],
                    phone=_["telephone"],
                    locator_domain=locator_domain,
                    location_type=", ".join(_.get("channel_types", [])),
                )


if __name__ == "__main__":
    with SgWriter(
        SgRecordDeduper(
            RecommendedRecordIds.StoreNumberId, duplicate_streak_failure_factor=200
        )
    ) as writer:
        search = DynamicGeoSearch(
            country_codes=SearchableCountries.ALL, expected_search_radius_miles=500
        )
        results = fetch_data(search)
        for rec in results:
            writer.write_row(rec)
