from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sglogging import SgLogSetup
import re
from sgscrape.sgpostal import parse_address_intl

logger = SgLogSetup().get_logger("catchairparty")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://catchairparty.com"
base_url = "https://catchairparty.com/locations/"


def fetch_data():
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        links = soup.select("div.location_btm")
        logger.info(f"{len(links)} found")
        for link in links:
            if "Coming Soon" in link.h4.text:
                continue
            page_url = link.h4.a["href"]
            logger.info(page_url)
            sp1 = bs(session.get(page_url, headers=_headers).text, "lxml")
            block = list(link.p.stripped_strings)
            addr = parse_address_intl(block[0])
            street_address = addr.street_address_1
            if addr.street_address_2:
                street_address += " " + addr.street_address_2
            hours = []
            _hr = sp1.find("h2", string=re.compile(r"STORE HOURS"))
            if _hr:
                hours = [hh.text.strip() for hh in _hr.find_next_siblings("p")]
                if hours and "Open" in hours[0]:
                    del hours[0]
            yield SgRecord(
                page_url=page_url,
                location_name=link.h4.text.strip(),
                street_address=street_address,
                city=addr.city,
                state=addr.state,
                zip_postal=addr.postcode,
                country_code="US",
                phone=block[1].replace("|", "").strip(),
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours).replace("–", "-"),
            )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
