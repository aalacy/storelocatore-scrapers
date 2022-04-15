from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
import json
import re

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}
locator_domain = "https://www.nptpool.com"
base_url = "https://www.nptpool.com/showrooms/"


def fetch_data():
    with SgRequests() as session:
        res = session.get(base_url, headers=_headers).text
        sp1 = bs(res, "lxml")
        locations = json.loads(
            res.split("var locations =")[1].split("var states")[0].strip()[:-1]
        )
        for _ in locations:
            modal = sp1.select_one(f"div#locationModal{_['id']}")
            _hr = modal.find("h5", string=re.compile(r"^Business Hours"))
            hours = []
            if _hr:
                hours = _hr.find_next_sibling("p").stripped_strings
            yield SgRecord(
                page_url=base_url,
                store_number=_["id"],
                location_name=_["name"],
                street_address=_["address"],
                city=_["city"],
                state=_["state"],
                latitude=_["latitude"],
                longitude=_["longitude"],
                zip_postal=_["zip"],
                phone=_["phone"],
                country_code=_["country"],
                locator_domain=locator_domain,
                raw_address=_["full_address"],
                hours_of_operation="; ".join(hours),
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
