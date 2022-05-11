from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from bs4 import BeautifulSoup as bs

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}
locator_domain = "https://www.saborlatingrill.com"
base_url = "https://www.saborlatingrill.com/wp-json/sf/locator/v1/list"
page_url = "https://www.saborlatingrill.com/locations/"


def fetch_data():
    with SgRequests() as session:
        locations = session.get(base_url, headers=_headers).json()["features"]
        for loc in locations:
            _ = loc["properties"]
            temp = list(bs(_["hours"], "lxml").stripped_strings)
            hours = []
            for x in range(0, len(temp), 2):
                hours.append(f"{temp[x]} {temp[x+1]}")
            addr = _["address"].split(",")
            yield SgRecord(
                page_url=page_url,
                store_number=loc["id"].split("_")[-1],
                location_name=_["title"],
                street_address=_["street_address"],
                city=addr[0],
                state=addr[1].strip().split()[0].strip(),
                latitude=loc["geometry"]["coordinates"][0],
                longitude=loc["geometry"]["coordinates"][1],
                zip_postal=addr[1].strip().split()[-1].strip(),
                country_code="US",
                phone=_["telephone"],
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours),
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
