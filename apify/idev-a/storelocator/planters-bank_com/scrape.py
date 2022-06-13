from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
import re
from bs4 import BeautifulSoup as bs
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


def _p(val):
    if (
        val.replace("(", "")
        .replace(")", "")
        .replace("+", "")
        .replace("-", "")
        .replace(".", " ")
        .replace("to", "")
        .replace(" ", "")
        .strip()
        .isdigit()
    ):
        return val
    else:
        return ""


def fetch_data():
    locator_domain = "https://www.planters-bank.com/"
    base_url = "https://www.planters-bank.com/ajax/get-location-data?branch=true"
    with SgRequests() as session:
        locations = session.get(base_url, headers=_headers).json()
        for _ in locations["locations"]:
            street_address = _["address"]
            if _["address_two"]:
                street_address += " " + _["address_two"]
            _hr = bs(_["hours"], "lxml").find(
                "strong", string=re.compile(r"Lobby Hours")
            )
            hours = []
            if _hr:
                hours = list(_hr.find_parent().stripped_strings)[1:]
                if not hours:
                    temp = []
                    for hh in _hr.find_parent().find_next_siblings("div"):
                        if hh.a or not hh.text.strip():
                            break
                        temp.append(hh.text.strip())
                    for x in range(0, len(temp), 2):
                        hours.append(f"{temp[x]} {temp[x+1]}")
            phone = _["phone"]
            if not phone:
                for _phone in bs(_["hours"], "lxml").select("div", recursive=False):
                    if _p(_phone.text):
                        phone = _phone.text.strip()
                        break
            yield SgRecord(
                page_url=_["url"],
                location_name=_["name"],
                street_address=street_address,
                city=_["city"],
                state=_["state"],
                zip_postal=_["zip"],
                latitude=_["lat"],
                longitude=_["long"],
                country_code="US",
                phone=phone,
                location_type=", ".join(_["type"]),
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours),
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
