from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
import json

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


def _p(val):
    if val:
        return (
            val.replace("(", "")
            .replace(")", "")
            .replace("+", "")
            .replace("-", "")
            .replace(".", " ")
            .replace("to", "")
            .replace(" ", "")
            .strip()
            .isdigit()
        )
    else:
        return False


def _ii(locations, _):
    phone = ""
    hours = []
    for loc in locations:
        if loc.a.text.strip() == _["name"].strip():
            phone = (
                loc.select("div.col-sm-6")[0]
                .select("p.text-display--small-p")[-1]
                .text.strip()
            )
            if not _p(phone):
                phone = ""
            hours = list(
                loc.select("div.col-sm-6")[1]
                .select_one("div.text-display--small-p")
                .stripped_strings
            )
            break
    return phone, hours


def fetch_data():
    locator_domain = "https://www.fsbwa.com"
    base_url = "https://www.fsbwa.com/locations"
    with SgRequests() as session:
        res = session.get(base_url, headers=_headers).text
        locations = bs(res, "lxml").select("li.locations-list__item")
        links = json.loads(
            res.split("window.locations =")[1].split("window.lat =")[0].strip()[:-1]
        )
        for _ in links:
            page_url = _["url"]
            street_address = _["address"]["address1"]
            if _["address"]["address2"]:
                street_address += " " + _["address"]["address2"]
            phone, hours = _ii(locations, _)
            location_type = ""
            if _["color"] == "blue":
                location_type = "Branch"
            if _["color"] == "orange":
                location_type = "Commercial Lending"
            if _["color"] == "green":
                location_type = "Home Lending"
            yield SgRecord(
                page_url=page_url,
                store_number=_["id"],
                location_name=_["name"],
                street_address=street_address,
                city=_["address"]["city"],
                state=_["address"]["state"],
                zip_postal=_["address"]["zip"],
                latitude=_["lat"],
                longitude=_["lng"],
                country_code="US",
                phone=phone,
                location_type=location_type,
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours),
                raw_address=_["address"]["formatted_address"],
            )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
