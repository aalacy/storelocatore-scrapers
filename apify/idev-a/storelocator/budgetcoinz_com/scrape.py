from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgpostal import parse_address_intl

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.budgetcoinz.com"
base_url = "https://api.storepoint.co/v1/15faedd9397770/locations?rq"


def fetch_data():
    with SgRequests() as session:
        locations = session.get(base_url, headers=_headers).json()["results"][
            "locations"
        ]
        for _ in locations:
            addr = parse_address_intl(_["streetaddress"])
            street_address = addr.street_address_1
            if addr.street_address_2:
                street_address += " " + addr.street_address_2
            yield SgRecord(
                page_url="https://www.budgetcoinz.com/locations/",
                store_number=_["id"],
                location_name=_["name"],
                street_address=street_address,
                city=addr.city,
                state=addr.state,
                zip_postal=addr.postcode,
                latitude=_["loc_lat"],
                longitude=_["loc_long"],
                country_code="US",
                phone=_["phone"],
                locator_domain=locator_domain,
                raw_address=_["streetaddress"],
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.GeoSpatialId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
