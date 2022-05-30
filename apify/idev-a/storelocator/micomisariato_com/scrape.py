from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://micomisariato.com"
base_url = "https://micomisariato.com/api/locales?offset=0&limit=9999"

types = {"1": "Hipermarket", "2": "Mi Comisariato", "3": "Mini"}


def fetch_data():
    with SgRequests() as session:
        locations = session.get(base_url, headers=_headers).json()["locales"]
        for _ in locations:
            raw_address = (
                _["direccion"].split("Km")[0].split("km")[0].replace("null", "").strip()
            )
            yield SgRecord(
                page_url="https://micomisariato.com/nuestros-locales-mas-cercanos",
                store_number=_["id"],
                location_name=_["nombre"],
                street_address=raw_address,
                latitude=_["latitud_gps"],
                longitude=_["longitud_gps"],
                country_code="Ecuador",
                location_type=types[str(_["categoria_id"])],
                locator_domain=locator_domain,
                hours_of_operation=_["horario"],
                raw_address=raw_address,
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
