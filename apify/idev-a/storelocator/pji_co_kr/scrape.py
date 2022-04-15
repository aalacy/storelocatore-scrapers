from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.pji.co.kr"
base_url = "https://www.pji.co.kr/searchStore"


def fetch_data():
    with SgRequests() as session:
        locations = session.get(base_url, headers=_headers).json()["list"]
        for _ in locations:
            hours = ""
            if _["openHh"]:
                hours = f"{_['openHh']}:{_['openMm']} - {_['closeHh']}:{_['closeMm']}"
            yield SgRecord(
                store_number=_["storeId"],
                location_name=_["name"],
                street_address=_["address"],
                city=_["addr2"],
                state=_["addr1"],
                latitude=_["yaxis"],
                longitude=_["xaxis"],
                phone=_["phone1"],
                locator_domain=locator_domain,
                hours_of_operation=hours,
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
