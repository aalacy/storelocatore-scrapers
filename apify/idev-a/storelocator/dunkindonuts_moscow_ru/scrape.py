from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sglogging import SgLogSetup
import dirtyjson as json
from sgscrape.sgpostal import parse_address_intl
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

logger = SgLogSetup().get_logger("dunkindonutsmoscow")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://dunkindonutsmoscow.ru"
base_url = "https://dunkindonutsmoscow.ru/cafe/"


def fetch_data():
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        links = soup.select("div.cafe-list div.cafe-item")
        logger.info(f"{len(links)} found")
        for link in links:
            page_url = locator_domain + link.a["href"]
            logger.info(page_url)
            ss = json.loads(
                session.get(page_url, headers=_headers)
                .text.split("BX_YMapAddPlacemark(map,")[1]
                .split(");")[0]
            )
            items = link.select("div.cafe-info__item")
            raw_address = list(items[0].stripped_strings)[1]
            addr = parse_address_intl(raw_address + ", Россия")
            street_address = addr.street_address_1
            if addr.street_address_2:
                street_address += " " + addr.street_address_2
            _p = list(items[2].stripped_strings)
            phone = ""
            if len(_p) > 1:
                phone = _p[1].strip()
            yield SgRecord(
                page_url=page_url,
                location_name=link.a.text.strip(),
                street_address=street_address,
                city=addr.city,
                state=addr.state,
                country_code="Russia",
                phone=phone,
                locator_domain=locator_domain,
                latitude=ss["LAT"],
                longitude=ss["LON"],
                hours_of_operation=list(items[3].stripped_strings)[1],
                raw_address=raw_address,
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
