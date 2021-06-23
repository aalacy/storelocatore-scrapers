from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
import json
from bs4 import BeautifulSoup as bs

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


def fetch_data():
    locator_domain = "https://servicefirstautomotive.com/"
    base_url = "https://servicefirstautomotive.com/locate-a-center"
    with SgRequests() as session:
        locations = json.loads(
            bs(session.get(base_url, headers=_headers).text, "lxml")
            .find("script", type="application/ld+json")
            .string
        )[0]["subOrganization"]
        for _ in locations:
            yield SgRecord(
                page_url=_["url"],
                location_name=_["name"].replace("–", "-").strip(),
                street_address=_["address"]["streetAddress"],
                city=_["address"]["addressLocality"],
                state=_["address"]["addressRegion"],
                zip_postal=_["address"]["postalCode"],
                latitude=_["geo"]["latitude"],
                longitude=_["geo"]["longitude"],
                country_code="US",
                location_type=_["@type"],
                phone=_["telephone"],
                locator_domain=locator_domain,
                hours_of_operation="; ".join(_["openingHours"]).replace("–", "-"),
            )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
