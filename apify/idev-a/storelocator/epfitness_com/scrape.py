from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sglogging import SgLogSetup
import re

logger = SgLogSetup().get_logger("epfitness")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


def fetch_data():
    locator_domain = "https://www.epfitness.com/"
    base_url = "https://www.epfitness.com/"
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        links = soup.select("nav ul li")[2].select("ul li a")
        logger.info(f"{len(links)} found")
        for link in links:
            page_url = link["href"]
            logger.info(page_url)
            sp1 = bs(session.get(page_url, headers=_headers).text, "lxml")
            h1 = sp1.find("h1")
            block = h1.find_parent().find_next_sibling().text.strip().split("|")
            addr = block[0].split(",")
            _hr = sp1.find("span", string=re.compile(r"Hours of Operation:"))
            hours = []
            if _hr:
                hours = [
                    hh.text.strip() for hh in _hr.find_parent().find_next_siblings()
                ]

            yield SgRecord(
                page_url=page_url,
                location_name=h1.text.strip(),
                street_address=addr[0].strip(),
                city=addr[1].strip(),
                state=addr[2].split(" ")[0].strip(),
                zip_postal=addr[2].split(" ")[-1].strip(),
                country_code="US",
                phone=block[1],
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours)
                .replace("–", "-")
                .replace("\xa0", ""),
            )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
