from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgscrape.sgpostal import parse_address_intl
from bs4 import BeautifulSoup as bs
import re
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("equinix")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


def fetch_data():
    locator_domain = "https://www.equinix.com/data-centers/"
    base_url = "https://www.equinix.com/data-centers/americas-colocation"
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        links = []
        links += (
            soup.select_one("h2#united-states").find_next_sibling("ul").select("li a")
        )
        links += soup.select_one("h2#canada").find_next_sibling("ul").select("li a")
        logger.info(f"[Links] {len(links)} found")
        for link in links:
            state_url = link["href"]
            sp1 = bs(session.get(state_url, headers=_headers).text, "lxml")
            locations = sp1.select("div.hero-slice-button-wrap div")[0].select("a")
            logger.info(f"[states] {len(locations)} found")
            for _ in locations:
                logger.info(f"{_['href']}")
                sp2 = bs(session.get(_["href"], headers=_headers).text, "lxml")
                location = sp2.select_one("div#eq-ibx-map")
                addr = parse_address_intl(location["data-ibx-address"])
                phone = sp2.find("a", href=re.compile(r"tel:")).text.strip()
                if phone == "NA":
                    phone = ""
                street_address = addr.street_address_1
                if addr.street_address_2:
                    street_address += ", " + addr.street_address_2
                country = addr.country
                if len(addr.postcode) > 5:
                    country = "CA"
                yield SgRecord(
                    page_url=_["href"],
                    location_name=sp2.h1.text,
                    street_address=street_address,
                    city=addr.city,
                    state=addr.state,
                    latitude=location["data-ibx-latitude"],
                    longitude=location["data-ibx-longitude"],
                    zip_postal=addr.postcode,
                    country_code=country,
                    phone=phone,
                    locator_domain=locator_domain,
                )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
