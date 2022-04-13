from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
import dirtyjson as json
from bs4 import BeautifulSoup as bs
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.castorama.ru"
base_url = "https://www.castorama.ru/stores"


def fetch_data():
    with SgRequests() as session:
        locations = session.get(base_url, headers=_headers).text.split("data.push(")[1:]
        for loc in locations:
            _ = json.loads(loc.split(");")[0])
            info = bs(_["properties"]["balloonContent"], "lxml")
            addr = list(info.select_one("p.address").stripped_strings)
            page_url = info.a["href"]
            logger.info(page_url)
            sp1 = bs(session.get(page_url, headers=_headers).text, "lxml")
            yield SgRecord(
                page_url=page_url,
                store_number=_["id"],
                location_name=info.select_one("p.shop-name").text.strip(),
                street_address=addr[0],
                city=info.select_one("p.city").text.strip(),
                zip_postal=sp1.select_one('meta[itemprop="postalCode"]')["content"],
                latitude=_["geometry"]["coordinates"][0],
                longitude=_["geometry"]["coordinates"][1],
                country_code="RU",
                phone=sp1.select_one('meta[itemprop="telephone"]')["content"],
                locator_domain=locator_domain,
                hours_of_operation=info.select_one("span.time-shop").text.strip(),
                raw_address=" ".join(addr),
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
