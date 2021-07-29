from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://movatiathletic.com"
base_url = "https://movatiathletic.com/wp-content/plugins/rp-locator/locations.json"


def fetch_data():
    with SgRequests() as session:
        locations = session.get(base_url, headers=_headers).json()
        for _ in locations:
            street_address = _["address1"]
            if _["address2"]:
                street_address += " " + _["address2"]
            yield SgRecord(
                page_url="https://movatiathletic.com/locations/",
                store_number=_["id"],
                location_name=_["name"],
                street_address=street_address.replace("East Kingsville Square", ""),
                city=_["city"],
                state=_["province"],
                zip_postal=_["postcode"],
                latitude=_["lat"],
                longitude=_["lon"],
                country_code="CA",
                phone=_["phone1"],
                location_type=_["type"],
                locator_domain=locator_domain,
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.GeoSpatialId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
