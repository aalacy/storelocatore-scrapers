from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sglogging import SgLogSetup
from sgzip.dynamic import DynamicGeoSearch
from sgpostal.sgpostal import parse_address_intl

logger = SgLogSetup().get_logger("")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "http://www.4fingers.com.my"
base_url = "https://4fingers.com.my/wp-admin/admin-ajax.php?action=store_search&lat={}&lng={}&max_results=25&search_radius=50"


def fetch_data(search):
    for lat, lng in search:
        with SgRequests() as session:
            locations = session.get(base_url.format(lat, lng), headers=_headers).json()[
                "store_data"
            ]
            logger.info(f"[{lat, lng}] {len(locations)}")
            for _ in locations:
                search.found_location_at(_["lat"], _["lng"])
                raw_address = _["address"]
                if "Malaysia" not in raw_address:
                    raw_address += ", Malaysia"
                addr = parse_address_intl(raw_address)
                street_address = addr.street_address_1
                if addr.street_address_2:
                    street_address += " " + addr.street_address_2
                yield SgRecord(
                    page_url=base_url,
                    store_number=_["id"],
                    location_name=_["store"],
                    street_address=street_address,
                    city=addr.city,
                    state=addr.state,
                    zip_postal=_["zip"],
                    country_code="MY",
                    phone=_["phone"],
                    latitude=_["lat"],
                    longitude=_["lng"],
                    locator_domain=locator_domain,
                    hours_of_operation=_["hours"],
                    raw_address=_["address"],
                )


if __name__ == "__main__":
    with SgWriter(
        SgRecordDeduper(
            SgRecordID({SgRecord.Headers.RAW_ADDRESS}),
            duplicate_streak_failure_factor=10,
        )
    ) as writer:
        search = DynamicGeoSearch(country_codes=["my"], expected_search_radius_miles=50)
        results = fetch_data(search)
        for rec in results:
            writer.write_row(rec)
