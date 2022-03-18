from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
import dirtyjson as json
from bs4 import BeautifulSoup as bs

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.selectfashion.co.uk"
base_url = "https://www.selectfashion.co.uk/store-finder"


def fetch_data():
    with SgRequests() as session:
        locations = json.loads(
            session.get(base_url, headers=_headers)
            .text.split(".amLocator(")[1]
            .split(");")[0]
            .strip()
        )["jsonLocations"]["items"]
        for _ in locations:
            info = bs(_["popup_html"], "lxml")
            street_address = info.select_one("p.address").text.strip()

            phone = ""
            if info.select_one("div.phone-block a"):
                phone = info.select_one("div.phone-block a").text.strip()
            name = info.select_one("div.amlocator-title").text.strip()
            yield SgRecord(
                page_url=base_url,
                store_number=_["id"],
                location_name=name,
                street_address=street_address,
                city=name.split("-")[0].strip(),
                latitude=_["lat"],
                longitude=_["lng"],
                country_code="UK",
                phone=phone,
                locator_domain=locator_domain,
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
