from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sglogging import SgLogSetup
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgzip.dynamic import DynamicGeoSearch, SearchableCountries

logger = SgLogSetup().get_logger("toms.com")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.toms.com"
base_url = "https://www.toms.com/on/demandware.store/Sites-toms-us-Site/en_US/Stores-FindStores?showMap=true&radius=50&categories=&typesStores=&lat={}&long={}"


def fetch_data(search):
    for lat, lng in search:
        with SgRequests() as session:
            locations = session.get(base_url.format(lat, lng), headers=_headers).json()[
                "stores"
            ]
            logger.info(f"[{search.current_country()}] [{lat, lng}] {len(locations)}")
            for _ in locations:
                search.found_location_at(_["latitude"], _["longitude"])
                street_address = _["address1"]
                if _["address2"]:
                    street_address += " " + _["address2"]

                yield SgRecord(
                    page_url="https://www.toms.com/us/store-locator",
                    store_number=_["ID"],
                    location_name=_["name"],
                    street_address=street_address.replace("\n", "").replace("\r", " "),
                    city=_.get("city"),
                    state=_.get("stateCode"),
                    zip_postal=_.get("postalCode"),
                    country_code=_["countryCode"],
                    phone=_.get("phone"),
                    latitude=_["latitude"],
                    longitude=_["longitude"],
                    locator_domain=locator_domain,
                )


if __name__ == "__main__":
    with SgWriter(
        SgRecordDeduper(
            RecommendedRecordIds.StoreNumberId, duplicate_streak_failure_factor=10
        )
    ) as writer:
        search = DynamicGeoSearch(country_codes=[SearchableCountries.USA])
        results = fetch_data(search)
        for rec in results:
            writer.write_row(rec)
