from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from bs4 import BeautifulSoup as bs
import re
import json
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("jeffersons")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://jeffersons.com"
base_url = "https://jeffersons.com/all-locations/"


def fetch_data():
    with SgRequests() as session:
        ajax = json.loads(
            session.get(base_url, headers=_headers)
            .text.split("var ASL_REMOTE =")[1]
            .split(";")[0]
        )
        ajax_url = f"{ajax['ajax_url']}?action=asl_load_stores&nonce={ajax['nonce']}&load_all=1&layout=1"
        locations = session.get(ajax_url, headers=_headers).json()
        for _ in locations:
            logger.info(_["website"])
            sp1 = bs(session.get(_["website"], headers=_headers).text, "lxml")
            hours = []
            _hr = sp1.find("h3", string=re.compile(r"^HOURS", re.IGNORECASE))
            if _hr:
                hours = [
                    "; ".join(hh.stripped_strings)
                    for hh in _hr.find_next_siblings("p")
                    if hh.text.strip()
                ]
            yield SgRecord(
                page_url=_["website"],
                store_number=_["id"],
                location_name=_["title"],
                street_address=_["street"],
                city=_["city"],
                state=_["state"],
                zip_postal=_["postal_code"],
                latitude=_["lat"],
                longitude=_["lng"],
                country_code=_["country"],
                phone=_["phone"],
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours).replace("–", "-"),
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
