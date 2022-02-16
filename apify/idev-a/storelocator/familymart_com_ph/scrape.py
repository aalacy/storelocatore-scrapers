from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from bs4 import BeautifulSoup as bs
from sgzip.dynamic import DynamicGeoSearch, SearchableCountries
from sglogging import SgLogSetup
from sgpostal.sgpostal import parse_address_intl

logger = SgLogSetup().get_logger("familymart")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://familymart.com.ph"
base_url = "https://familymart.com.ph/wp-admin/admin-ajax.php?action=store_search&lat={}&lng={}&max_results=25&search_radius=1000&autoload=1"


def fetch_data(search):
    with SgRequests() as session:
        for lat, lng in search:
            locations = session.get(base_url.format(lat, lng), headers=_headers).json()
            for _ in locations:
                hour = ""
                if _["description"]:
                    hour = (
                        bs(_["description"], "lxml").text.strip().split(":")[-1].strip()
                    )
                logger.info(f"[{lat, lng}] {len(locations)}")
                addr = parse_address_intl(_["address"] + ", Philippines")
                street_address = addr.street_address_1
                if addr.street_address_2:
                    street_address += " " + addr.street_address_2
                city = addr.city
                if city and "Zone" in city:
                    city = ""
                state = addr.state
                if state == "Qc.":
                    state = ""
                yield SgRecord(
                    page_url="https://familymart.com.ph/branches/",
                    store_number=_["id"],
                    location_name=_["store"],
                    street_address=", ".join(_["address"].split(",")[:-1]),
                    city=city,
                    state=state,
                    latitude=_["lat"],
                    longitude=_["lng"],
                    country_code="Philippines",
                    phone=_["phone"],
                    locator_domain=locator_domain,
                    hours_of_operation=hour.replace("\n", "; "),
                    raw_address=_["address"],
                )


if __name__ == "__main__":
    search = DynamicGeoSearch(
        country_codes=[SearchableCountries.PHILIPPINES],
        expected_search_radius_miles=500,
    )
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        results = fetch_data(search)
        for rec in results:
            writer.write_row(rec)
