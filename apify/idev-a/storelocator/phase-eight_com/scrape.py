from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgrequests.sgrequests import SgRequests
from sgzip.dynamic import DynamicGeoSearch
from bs4 import BeautifulSoup as bs
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.phase-eight.com"
base_url = "https://www.phase-eight.com/stores"


def fetch_records(http, search):
    for lat, lng in search:
        country = search.current_country()
        url = f"https://www.phase-eight.com/on/demandware.store/Sites-P8-UK-Site/en/Stores-FindStores?lat={lat}&long={lng}&standaloneStore=on&outlet=on&dwfrm_address_country={country.upper()}&postalCode="
        locations = http.get(url, headers=_headers).json()["stores"]
        if locations:
            search.found_location_at(lat, lng)
        logger.info(f"[{country}] [{lat, lng}] {len(locations)}")
        for _ in locations:
            street_address = _["address1"]
            if _["address2"]:
                street_address += " " + _["address2"]
            hours = []
            for hh in _["workTimes"]:
                hours.append(f"{hh['weekDay']}: {hh['value']}")
            yield SgRecord(
                page_url=locator_domain + _["storeUrl"],
                location_name=_["name"],
                store_number=_["ID"],
                street_address=street_address,
                city=_["city"],
                zip_postal=_["postalCode"],
                country_code=_["countryDisplayValue"],
                phone=_.get("phone"),
                latitude=_["latitude"],
                longitude=_["longitude"],
                location_type=_["storeType"],
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours),
            )


if __name__ == "__main__":
    with SgRequests() as http:
        countries = []
        for cc in bs(http.get(base_url, headers=_headers).text, "lxml").select(
            "select#country option"
        ):
            countries.append(cc["value"].lower())
        search = DynamicGeoSearch(
            country_codes=list(set(countries)), expected_search_radius_miles=100
        )
        with SgWriter(
            SgRecordDeduper(
                RecommendedRecordIds.StoreNumberId, duplicate_streak_failure_factor=10
            )
        ) as writer:
            for rec in fetch_records(http, search):
                writer.write_row(rec)
