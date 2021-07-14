from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sglogging import SgLogSetup
import re
from sgscrape.sgpostal import parse_address_intl

logger = SgLogSetup().get_logger("neighborhoodgoods")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


def fetch_data():
    locator_domain = "https://neighborhoodgoods.com"
    base_url = "https://neighborhoodgoods.com/pages/locations"
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        links = soup.select("div.storesList > a")
        logger.info(f"{len(links)} found")
        for link in links:
            page_url = locator_domain + link["href"]
            logger.info(page_url)
            sp1 = bs(session.get(page_url, headers=_headers).text, "lxml")
            addr = parse_address_intl(
                sp1.find("h3", string=re.compile(r"Location"))
                .find_next_sibling()
                .a.text
            )
            street_address = addr.street_address_1
            if addr.street_address_2:
                street_address += " " + addr.street_address_2
            hours = [
                "".join(hh.stripped_strings)
                for hh in sp1.find("h3", string=re.compile(r"Location"))
                .find_next_sibling("ul")
                .select("li")
            ]
            yield SgRecord(
                page_url=page_url,
                location_name=sp1.h1.text.strip(),
                street_address=street_address,
                city=addr.city,
                state=addr.state,
                zip_postal=addr.postcode,
                country_code="US",
                phone=sp1.find("h3", string=re.compile(r"Contact"))
                .find_next_sibling()
                .strong.text.strip(),
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours).replace("–", "-"),
            )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
