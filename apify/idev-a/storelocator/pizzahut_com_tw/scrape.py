from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
import dirtyjson as json

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.pizzahut.com.tw"
base_url = "https://www.pizzahut.com.tw/order/menu/store_info_2019.js?v=n_20210127276"


def fetch_data():
    with SgRequests() as session:
        locations = json.loads(
            session.get(base_url, headers=_headers)
            .text.split("sdata=")[-1]
            .strip()[:-1]
        )
        for key, _ in locations.items():
            yield SgRecord(
                page_url="",
                store_number=key,
                location_name=_["n"],
                street_address=_["r"],
                city=_["a"],
                state=_["c"].replace(",", ""),
                country_code="Taiwan",
                phone=_["t"],
                locator_domain=locator_domain,
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
