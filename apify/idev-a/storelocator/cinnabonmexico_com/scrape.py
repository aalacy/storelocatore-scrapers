from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://cinnabonmexico.com"
base_url = "https://cinnabonmexico.com/json"


def fetch_data():
    with SgRequests() as session:
        locations = session.get(base_url, headers=_headers).json()
        for _ in locations:
            yield SgRecord(
                page_url="https://cinnabonmexico.com/ubicaciones",
                store_number=_["id"],
                location_name=_["nombre"],
                street_address=_["calle"] + " " + _["colonia"],
                state=_["entidad_federativa"],
                zip_postal=_["codigo_postal"],
                latitude=_["lat"],
                longitude=_["lng"],
                country_code="Mexico",
                locator_domain=locator_domain,
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.GeoSpatialId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
