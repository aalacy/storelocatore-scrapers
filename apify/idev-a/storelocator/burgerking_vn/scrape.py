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

locator_domain = "https://burgerking.vn"
base_url = "https://burgerking.vn/storepickup"


def fetch_data():
    with SgRequests() as session:
        locations = json.loads(
            session.get(base_url, headers=_headers)
            .text.split("var listStoreJson =")[1]
            .split(";</script>")[0]
            .strip()
        )
        for _ in locations:
            addr = _["address"].split(",")
            yield SgRecord(
                page_url=_["store_view_url"],
                store_number=_["store_id"],
                location_name=_["store_name"],
                street_address=", ".join(addr[:-1]),
                city=addr[-1],
                latitude=_["store_latitude"],
                longitude=_["store_longitude"],
                country_code="Vietnam",
                phone=_["store_phone"],
                locator_domain=locator_domain,
                hours_of_operation=":".join(
                    bs(_["description"], "lxml").text.split(":")[1:]
                )
                .replace("\xa0", " ")
                .replace(")", "")
                .strip(),
                raw_address=_["address"],
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
