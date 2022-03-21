from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
import json

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://bonaventuresenior.com"
base_url = "https://bonaventuresenior.com/communities/"


def fetch_data():
    with SgRequests() as session:
        locations = json.loads(
            session.get(base_url, headers=_headers)
            .text.split("var location_tool =")[1]
            .split("/* ]]> */")[0]
            .strip()[:-1]
        )["locations"]
        for _ in locations:
            yield SgRecord(
                page_url=_["url"],
                location_name=_["name"],
                street_address=_["street"],
                city=_["city"],
                state=_["state"],
                zip_postal=_["zip"],
                latitude=_["latitude"],
                longitude=_["longitude"],
                country_code="US",
                phone=_["phone"],
                locator_domain=locator_domain,
                raw_address=_["address"],
            )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
