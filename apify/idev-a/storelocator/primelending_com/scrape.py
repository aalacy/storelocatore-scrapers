from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
import json

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


def fetch_data():
    locator_domain = "https://www.primelending.com/"
    base_url = "https://lo.primelending.com/lo.jsonp?_=1623438890940"
    with SgRequests() as session:
        locations = json.loads(
            session.get(base_url, headers=_headers)
            .text.split("loJsonCallback(")[1]
            .strip()[:-1]
        )
        for _ in locations:
            yield SgRecord(
                page_url=_["branchWebsite"],
                location_name=_["name"],
                street_address=_["streetAddress"],
                city=_["city"],
                state=_["state"],
                zip_postal=_["zip"],
                latitude=_["lat"],
                longitude=_["lng"],
                country_code="US",
                phone=_["telephone"],
                locator_domain=locator_domain,
                raw_address=_["address"],
            )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
