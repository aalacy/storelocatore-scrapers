from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.gaes.cl"

base_url = "https://www.gaesargentina.com.ar/ajax/getcentersjson?lat=23.634501&long=-102.552784&ratio=10000&pais=ARGENTINA&provincia="

countries = [
    "ARGENTINA",
    "CHILE",
    "COLOMBIA",
    "ECUADOR",
    "MEXICO",
]

urls = {
    "ARGENTINA": "https://www.gaesargentina.com.ar/localizador-centros-auditivos-gaes",
    "CHILE": "https://www.gaes.cl/localizador-centros-auditivos-gaes",
    "COLOMBIA": "https://www.gaes.co/localizador-centros-auditivos-gaes",
    "ECUADOR": "https://www.gaes.ec/localizador-centros-auditivos-gaes",
    "MEXICO": "https://www.gaes.com.mx/localizador-centros-auditivos-gaes",
}


def fetch_data():
    with SgRequests() as session:
        locations = session.get(base_url, headers=_headers).json()["centros"]
        for _ in locations:
            if _["country"] not in countries:
                continue

            yield SgRecord(
                page_url=urls[_["country"]],
                store_number=_["id"],
                location_name=_["name"],
                street_address=_["address"],
                city=_["ciudad"],
                state=_.get("provincia"),
                zip_postal=_["zip"],
                latitude=_["lat"],
                longitude=_["long"],
                country_code=_["country"],
                phone=_["phone"],
                locator_domain=locator_domain,
                hours_of_operation=_["horario"],
            )


if __name__ == "__main__":
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {
                    SgRecord.Headers.STORE_NUMBER,
                    SgRecord.Headers.LATITUDE,
                    SgRecord.Headers.LONGITUDE,
                }
            )
        )
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
