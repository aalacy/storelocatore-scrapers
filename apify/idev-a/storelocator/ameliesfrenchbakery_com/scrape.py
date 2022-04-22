from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sglogging import SgLogSetup
import re
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgpostal.sgpostal import parse_address_intl

logger = SgLogSetup().get_logger("ameliesfrenchbakery")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}
locator_domain = "https://ameliesfrenchbakery.com"
base_url = "https://ameliesfrenchbakery.com/"


def fetch_data():
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        links = soup.select("div#main-navigation-wrapper li.dropdown ul")[0].select("a")
        logger.info(f"{len(links)} found")
        for link in links:
            page_url = locator_domain + link["href"]
            logger.info(page_url)
            sp1 = bs(session.get(page_url, headers=_headers).text, "lxml")
            _bb = sp1.find("h3", string=re.compile(r"Stop by our location"))
            block = list(_bb.find_next_sibling().stripped_strings)
            raw_address = block[0]
            addr = parse_address_intl(raw_address + ", United States")
            street_address = addr.street_address_1
            if addr.street_address_2:
                street_address += " " + addr.street_address_2
            hours = []
            if len(block) == 1:
                hours = [_bb.find_next_sibling().find_next_sibling().text.strip()]
            else:
                hours = block[1:]

            yield SgRecord(
                page_url=page_url,
                location_name=link.text.strip(),
                street_address=street_address,
                city=addr.city,
                state=addr.state,
                zip_postal=addr.postcode,
                country_code="US",
                phone=sp1.find("a", href=re.compile(r"tel:")).text.strip(),
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours),
                raw_address=raw_address,
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
