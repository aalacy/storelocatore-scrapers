from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sglogging import SgLogSetup
import re

logger = SgLogSetup().get_logger("ameliesfrenchbakery")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


def fetch_data():
    locator_domain = "https://ameliesfrenchbakery.com"
    base_url = "https://ameliesfrenchbakery.com/locations/"
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        links = soup.select("ul.uabb-cl-ul li a")
        logger.info(f"{len(links)} found")
        for link in links:
            page_url = locator_domain + link["href"]
            logger.info(page_url)
            sp1 = bs(session.get(page_url, headers=_headers).text, "lxml")
            block = sp1.select(".fl-module-content.fl-node-content .fl-rich-text")[0]
            addr = [
                aa.replace("\xa0", " ") for aa in block.select("p")[0].stripped_strings
            ]
            _hr = sp1.find("strong", string=re.compile(r"Hours"))
            hours = []
            if _hr:
                if _hr.find_parent().find_next_sibling("p"):
                    temp = list(
                        _hr.find_parent().find_next_sibling("p").stripped_strings
                    )
                    if len(temp) > 1:
                        for x in range(0, len(temp), 2):
                            hours.append(f"{temp[x]} {temp[x+1]}")
                    else:
                        hours = temp
            else:
                _hr = sp1.find("", string=re.compile(r"Hours"))
                if _hr:
                    hours = list(_hr.find_parent().find_parent().stripped_strings)[1:]
            coord = (
                sp1.select_one("div.fl-html iframe")["src"]
                .split("!2d")[1]
                .split("!3m")[0]
                .split("!3d")
            )
            yield SgRecord(
                page_url=page_url,
                location_name=link.text.strip(),
                street_address=addr[0],
                city=addr[1].split(",")[0].strip(),
                state=addr[1].split(",")[1].strip().split(" ")[0].strip(),
                zip_postal=addr[1].split(",")[1].strip().split(" ")[-1].strip(),
                country_code="US",
                phone=sp1.find("a", href=re.compile(r"tel:")).text.strip(),
                locator_domain=locator_domain,
                latitude=coord[1],
                longitude=coord[0],
                hours_of_operation="; ".join(hours).replace("–", "-"),
            )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
