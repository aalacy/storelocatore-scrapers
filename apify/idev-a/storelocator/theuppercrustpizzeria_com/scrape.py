from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sglogging import SgLogSetup
import re

logger = SgLogSetup().get_logger("theuppercrustpizzeria")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.theuppercrustpizzeria.com"
base_url = "https://www.theuppercrustpizzeria.com/locations/"


def fetch_data():
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        links = soup.select("div.location-box")
        logger.info(f"{len(links)} found")
        for link in links:
            page_url = locator_domain + link.a["href"]
            logger.info(page_url)
            addr = link.select_one("p.location-desc").text.strip().split(",")
            sp1 = bs(session.get(page_url, headers=_headers).text, "lxml")
            hours = []
            if sp1.find_all("h3", string=re.compile(r"Hours")):
                _hr = sp1.find_all("h3", string=re.compile(r"Hours"))[-1]
                if _hr:
                    hours = [
                        hh.strip()
                        for hh in _hr.next_siblings
                        if not hh.name and hh.strip()
                    ]

            phone = ""
            if sp1.find("a", href=re.compile(r"tel:")):
                phone = sp1.find("a", href=re.compile(r"tel:")).text
            yield SgRecord(
                page_url=page_url,
                location_name=link.h2.text.strip(),
                street_address=addr[0],
                city=addr[1].strip(),
                state=addr[2].strip().split(" ")[0].strip(),
                zip_postal=addr[2].strip().split(" ")[-1].strip(),
                country_code="US",
                phone=phone,
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours),
            )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
