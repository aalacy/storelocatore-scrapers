from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://telekom.mk/"
base_url = "https://www.telekom.mk/services/ShopsGMapService_New.asmx/GetShopsGoogleMap"


def fetch_data():
    with SgRequests() as session:
        payload = {"Language": ""}
        locations = session.post(base_url, headers=_headers, json=payload).json()["d"]
        for _ in locations:
            yield SgRecord(
                page_url="https://www.telekom.mk/telekom-prodavnici.nspx",
                store_number=_["ID"],
                location_name=_["MESTO"],
                street_address=_["ADRESA"],
                city=_["MESTO"],
                latitude=_["LATITUDE"],
                longitude=_["LONGITUDE"],
                country_code="Macedonia",
                locator_domain=locator_domain,
                hours_of_operation=_["RABOTNO_VREME"],
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
