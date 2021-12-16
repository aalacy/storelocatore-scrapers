from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sglogging import SgLogSetup
from sgzip.dynamic import DynamicGeoSearch, SearchableCountries
from tenacity import retry, wait_fixed, stop_after_attempt

logger = SgLogSetup().get_logger("shell")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.shell.ae/"
json_url = "https://shellgsllocator.geoapp.me/api/v1/locations/nearest_to?lat={}&lng={}&autoload=true&travel_mode=driving&avoid_tolls=false&avoid_highways=false&avoid_ferries=false&corridor_radius=500&driving_distances=false&format=json"


@retry(wait=wait_fixed(2), stop=stop_after_attempt(3))
def get_json(url):
    with SgRequests(proxy_country="us") as session:
        return session.get(url, headers=_headers).json()


def fetch_data(search):
    for lat, lng in search:
        try:
            locations = get_json(json_url.format(lat, lng))
            logger.info(f"[{search.current_country()}] [{lat, lng}] {len(locations)}")
        except:
            logger.warning(f"[{search.current_country()}] [{lat, lng}] ==========")
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
            RecommendedRecordIds.StoreNumberId, duplicate_streak_failure_factor=2000
        )
    ) as writer:
        search = DynamicGeoSearch(country_codes=SearchableCountries.ALL)
        results = fetch_data(search)
        for rec in results:
            writer.write_row(rec)
