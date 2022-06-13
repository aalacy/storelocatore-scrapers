from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from bs4 import BeautifulSoup as bs

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://retailmap.pl/pl/centra-handlowe"
base_url = "https://retailmap.pl/pl/api/malls/?areaFrom=&areaTo=&name=&streetName=&status%5B%5D=existing"


def fetch_data():
    with SgRequests() as session:
        locations = session.get(base_url, headers=_headers).json()
        for _ in locations:
            addr = _["address"]
            street_address = addr["streetName"]
            if addr["streetNumber"]:
                street_address += " " + addr["streetNumber"]
            page_url = "https://retailmap.pl" + bs(_["html"], "lxml").a["href"]
            yield SgRecord(
                page_url=page_url,
                store_number=_["id"],
                location_name=_["name"],
                street_address=street_address,
                city=addr["city"],
                latitude=_["location"]["lat"],
                longitude=_["location"]["lng"],
                country_code="Poland",
                locator_domain=locator_domain,
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
