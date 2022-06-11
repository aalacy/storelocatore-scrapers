from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sglogging import SgLogSetup
import re

logger = SgLogSetup().get_logger("factorydonuts")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


def fetch_data():
    locator_domain = "https://factorydonuts.com"
    base_url = "https://factorydonuts.com/locations//"
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        links = soup.select(
            "div#fl-main-content div.fl-node-content div.fl-col-small .fl-module"
        )
        logger.info(f"{len(links)} found")
        for link in links:
            if link.p.strong and "Coming Soon" in link.p.strong.text:
                continue
            page_url = link.h5.a["href"]
            logger.info(page_url)
            res = session.get(page_url, headers=_headers)
            sp1 = bs(res.text, "lxml")
            addr = list(link.p.stripped_strings)[:-1]
            temp = list(
                sp1.find("span", string=re.compile(r"^HOURS"))
                .find_parent()
                .find_parent()
                .find_parent()
                .find_next_sibling("div")
                .stripped_strings
            )
            hours = []
            for x in range(0, len(temp), 2):
                hours.append(f"{temp[x]} {temp[x+1]}")
            yield SgRecord(
                page_url=res.url,
                location_name=link.strong.text.strip(),
                street_address=" ".join(addr[:-1]),
                city=addr[-1].split(",")[0].strip(),
                state=addr[-1].split(",")[1].strip().split(" ")[0].strip(),
                zip_postal=addr[-1].split(",")[1].strip().split(" ")[-1].strip(),
                country_code="US",
                phone=sp1.find("a", href=re.compile(r"tel:")).text.strip(),
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours).replace("–", "-"),
            )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
