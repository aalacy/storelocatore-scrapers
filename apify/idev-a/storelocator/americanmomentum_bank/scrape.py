from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
import re

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


def fetch_data():
    locator_domain = "https://www.americanmomentum.bank"
    base_url = "https://www.americanmomentum.bank/about-us/locations-hours.html"
    with SgRequests() as session:
        locations = bs(session.get(base_url, headers=_headers).text, "lxml").select(
            "ul#locList li"
        )
        for _ in locations:
            page_url = locator_domain + _.select_one("a.seeDetails")["href"]
            street_address = _["data-address1"]
            if _["data-address2"]:
                street_address += " " + _["data-address2"]
            location_type = ["branch"]
            if _.select_one("span.hasATM"):
                location_type.append(_.select_one("span.hasATM").text.strip())
            hours = []
            _hr = list(_.select_one("div.lobbyHours").stripped_strings)
            if _hr:
                temp = list(_hr)[1:]
                for x in range(0, len(temp), 2):
                    hours.append(f"{temp[x]} {temp[x+1]}")

            _phone = _.find("span", string=re.compile(r"Phone"))
            phone = ""
            if _phone:
                phone = _phone.find_next_sibling().text.strip()
            yield SgRecord(
                page_url=page_url,
                location_name=_["data-title"],
                street_address=street_address,
                city=_["data-city"],
                state=_["data-state"],
                zip_postal=_["data-zip"],
                latitude=_["data-latitude"],
                longitude=_["data-longitude"],
                country_code="US",
                phone=phone,
                location_type=", ".join(location_type),
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours),
            )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
