from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://blnts.com"
base_url = "https://blnts.com/apps/api/v1/stores?&_=1626156890220"
page_url = "https://blnts.com/pages/find-a-store"


def fetch_data():
    with SgRequests() as session:
        locations = session.get(base_url, headers=_headers).json()["stores"]
        for _ in locations:
            street_address = _["address"]["line1"]
            if _["address"]["line2"]:
                street_address += " " + _["address"]["line2"]
            if _["address"]["line3"]:
                street_address += " " + _["address"]["line3"]
            hours = [
                f"{hh['day']}: {hh['open_time']}:{hh['close_time']}"
                for hh in _["open_hours"]
            ]
            if _["temporarily_closed"]:
                hours = ["temporarily closed"]
            yield SgRecord(
                page_url=page_url,
                store_number=_["store_code"],
                location_name=_["address"]["name"],
                street_address=street_address,
                city=_["address"]["city"],
                state=_["address"]["state"],
                zip_postal=_["address"]["zip"],
                latitude=_["address"]["latitude"],
                longitude=_["address"]["longitude"],
                country_code="CA",
                phone=_["phone"],
                location_type=_["brand"],
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours),
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
