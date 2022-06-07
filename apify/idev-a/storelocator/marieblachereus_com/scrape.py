from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
import json
import re
from bs4 import BeautifulSoup as bs

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.marieblachereus.com"
base_url = "https://www.marieblachereus.com/hours-and-locations/"


def fetch_data():
    with SgRequests() as session:
        locations = json.loads(
            session.get(base_url, headers=_headers)
            .text.split("locations:")[1]
            .split("apiKey")[0]
            .strip()[:-1]
        )
        for _ in locations:
            if "Opening Soon" in _["hours"]:
                continue
            hr = bs(_["hours"], "lxml").find("h3", string=re.compile(r"Daily"))
            hours = ""
            if hr:
                hours = hr.find_next_sibling().text.strip()
            yield SgRecord(
                page_url=locator_domain + _["url"],
                store_number=_["id"],
                location_name=_["name"],
                street_address=_["street"],
                city=_["city"],
                state=_["state"],
                zip_postal=_["postal_code"],
                latitude=_["lat"],
                longitude=_["lng"],
                country_code="US",
                phone=_["phone_number"],
                locator_domain=locator_domain,
                hours_of_operation=hours,
                raw_address=_["address"],
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
