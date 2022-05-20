from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.zipcar.com"
base_url = "https://www.zipcar.com/api/drupal/1.0/presales-api/markets"


def fetch_data():
    with SgRequests() as session:
        locations = session.get(base_url, headers=_headers).json()["markets"]
        for _ in locations:
            yield SgRecord(
                page_url="https://www.zipcar.com/cities",
                store_number=_["marketId"],
                location_name=_["name"],
                latitude=_["latitude"],
                longitude=_["longitude"],
                country_code=_["countryIso"],
                locator_domain=locator_domain,
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.GeoSpatialId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
