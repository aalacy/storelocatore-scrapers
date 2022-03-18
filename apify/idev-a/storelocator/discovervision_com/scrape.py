from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
import dirtyjson as json

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


base_url = "https://www.discovervision.com/locations/"
locator_domain = "https://www.discovervision.com/"


def fetch_data():
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        locations = json.loads(soup.find("script", type="application/ld+json").string)[
            "location"
        ]
        for _ in locations:
            addr = _["address"]
            street_address = addr["streetAddress"].strip()
            if street_address.endswith(","):
                street_address = street_address[:-1].strip()
            coord = _["hasMap"].split("/@")[1].split("/data")[0].split(",")
            yield SgRecord(
                page_url=_["url"],
                location_name=_["name"],
                street_address=street_address,
                city=addr["addressLocality"],
                state=addr["addressRegion"],
                zip_postal=addr["postalCode"],
                latitude=coord[0],
                longitude=coord[1],
                country_code="US",
                phone=_["telephone"],
                locator_domain=locator_domain,
                hours_of_operation="; ".join(_["openingHours"]),
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
