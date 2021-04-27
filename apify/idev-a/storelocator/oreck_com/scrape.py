from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
import json
from bs4 import BeautifulSoup as bs

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


def _hours(temp, name):
    hours = []
    for key, hh in temp.items():
        if key == name.strip():
            for day, times in hh.items():
                hours.append(f"{day}: {times}")

    return hours


def fetch_data():
    locator_domain = "https://oreck.com/"
    base_url = "https://oreck.com/pages/find-your-local-store"
    with SgRequests() as session:
        data = json.loads(
            bs(session.get(base_url, headers=_headers).text, "lxml")
            .find_all("script", type="application/json")[-1]
            .string.strip()
        )
        for _ in data["authorizedStores"]:
            yield SgRecord(
                page_url=base_url,
                location_name=_["n"],
                street_address=_["a1"],
                city=_["c"],
                state=_["s"],
                zip_postal=_["z"],
                latitude=_["lat"],
                longitude=_["lng"],
                country_code="US",
                phone=_["p"],
                locator_domain=locator_domain,
                hours_of_operation="; ".join(_hours(data["storeHours"], _["n"])),
            )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
