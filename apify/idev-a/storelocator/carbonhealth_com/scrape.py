from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
import json
from bs4 import BeautifulSoup as bs

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]


def fetch_data():
    locator_domain = "https://carbonhealth.com/"
    base_url = "https://carbonhealth.com/locations"
    with SgRequests() as session:
        locations = json.loads(
            bs(session.get(base_url, headers=_headers).text, "lxml")
            .select_one("script#__NEXT_DATA__")
            .string
        )
        for _ in locations["props"]["initialState"]["config"]["locations"]:
            if _["typ"] == "Vaccination":
                continue
            page_url = locator_domain + _["slug"]
            hours = []
            for k, _hr in _["specialties"].items():
                if _hr["name"] == "Primary Care":
                    for hh in _hr["hours"]:
                        hours.append(f"{days[hh['day']]}: {hh['from']}-{hh['to']}")
            yield SgRecord(
                page_url=page_url,
                location_name=_["name"],
                street_address=_["address"]["firstLine"],
                city=_["address"]["city"],
                state=_["address"]["state"],
                zip_postal=_["address"]["zip"],
                latitude=_["address"]["latitude"],
                longitude=_["address"]["longitude"],
                country_code="US",
                phone=_.get("phoneNumber"),
                location_type=_["typ"],
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours),
            )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
