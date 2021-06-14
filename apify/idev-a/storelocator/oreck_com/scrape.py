from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
import json
from bs4 import BeautifulSoup as bs

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


def fetch_data():
    locator_domain = "https://oreck.com/"
    base_url = "https://oreck.com/pages/find-your-local-store"
    with SgRequests() as session:
        data = json.loads(
            bs(session.get(base_url, headers=_headers).text, "lxml")
            .find_all("script", type="application/json")[-1]
            .string.strip()
        )
        for x, group in data["storeGroups"].items():
            for _ in group:
                yield SgRecord(
                    page_url=base_url,
                    location_name=_["n"].strip(),
                    street_address=_["a1"],
                    city=_["c"],
                    state=_["s"],
                    zip_postal=_["z"],
                    latitude=_["lat"],
                    longitude=_["lng"],
                    country_code="US",
                    phone=_["p"],
                    locator_domain=locator_domain,
                )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
