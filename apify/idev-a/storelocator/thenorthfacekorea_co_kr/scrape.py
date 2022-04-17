from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
import json
from bs4 import BeautifulSoup as bs

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.thenorthfacekorea.co.kr"
base_url = "https://www.thenorthfacekorea.co.kr/store"


def fetch_data():
    with SgRequests() as session:
        locations = json.loads(
            bs(session.get(base_url, headers=_headers).text, "lxml")
            .select_one("div.store-content-container")
            .findChildren(recursive=False)[0]["data-store-list"]
            .replace("&quot;", '"')
        )
        for _ in locations:
            raw_address = _["address1"]
            if _["address2"]:
                raw_address += " " + _["address2"]
            _ss = raw_address.replace(_["state"], "").strip().split(_["city"])
            if len(_ss) > 1:
                street_address = _["city"].join(_ss[1:])
            else:
                street_address = _ss[-1]

            hours = _["holidayClosedDates"]
            if not hours:
                hours = ["별도 휴무일이 없습니다"]
            yield SgRecord(
                page_url=base_url,
                store_number=_["id"],
                location_name=_["name"],
                street_address=street_address,
                city=_["city"],
                state=_["state"],
                zip_postal=_["zip"],
                latitude=_["latitude"],
                longitude=_["longitude"],
                country_code="KR",
                phone=_["phone"],
                locator_domain=locator_domain,
                location_type=_["customTaxonomy"],
                hours_of_operation="; ".join(hours),
                raw_address=raw_address,
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
