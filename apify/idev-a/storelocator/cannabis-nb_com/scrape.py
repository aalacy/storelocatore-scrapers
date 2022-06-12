from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
import dirtyjson as json
from bs4 import BeautifulSoup as bs

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.cannabis-nb.com"
base_url = "https://www.cannabis-nb.com/stores/"


def _ii(links, _):
    hours = []
    for link in links:
        if _["name"] == link.td.text.strip():
            hours = list(link.select("td")[-1].stripped_strings)
            break
    return hours


def fetch_data():
    with SgRequests() as session:
        res = session.get(base_url, headers=_headers).text
        links = bs(res, "lxml").select("div.storeLocator div.visible-lg table tbody tr")
        locations = res.replace("pinImage", "'pinImage'").split("markers.push(")[1:]
        for loc in locations:
            _ = json.loads(loc.split("totalLat +=")[0].strip()[:-2])
            street_address = " ".join(_["address"].split(",")[:-3])
            state = _["address"].split(",")[-2].strip().split(" ")[0].strip()
            hours = _ii(links, _)
            yield SgRecord(
                page_url=base_url,
                location_name=_["name"],
                street_address=street_address,
                city=_["city"],
                state=state,
                zip_postal=_["zipCode"],
                latitude=_["coords"]["lat"],
                longitude=_["coords"]["lng"],
                country_code="CA",
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours),
            )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
