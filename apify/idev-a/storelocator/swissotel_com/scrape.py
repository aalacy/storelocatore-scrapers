from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sglogging import SgLogSetup
from sgscrape.sgpostal import parse_address_intl
import re

logger = SgLogSetup().get_logger("swissotel")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.swissotel.com"
base_url = "https://www.swissotel.com/destinations/"


def fetch_data():
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        links = soup.select("div#map-listings li.listing-row a")
        logger.info(f"{len(links)} found")
        for link in links:
            page_url = link["href"]
            if not page_url.startswith("http"):
                page_url = locator_domain + page_url
            logger.info(page_url)
            sp1 = bs(session.get(page_url, headers=_headers).text, "lxml")
            temp = []
            for aa in sp1.select("address p"):
                if "phone" in aa.text.lower():
                    break
                temp.append(aa.text.strip())
            addr = parse_address_intl(" ".join(temp))
            street_address = addr.street_address_1
            if addr.street_address_2:
                street_address += " " + addr.street_address_2
            phone = ""
            if sp1.find("p", string=re.compile(r"Telephone")):
                phone = (
                    list(
                        sp1.find("p", string=re.compile(r"Telephone")).stripped_strings
                    )[0]
                    .split(":")[-1]
                    .replace("Telephone", "")
                    .replace("TBD", "")
                    .strip()
                )
            yield SgRecord(
                page_url=page_url,
                location_name=sp1.select_one("#imgPropertyLogoAddress")["alt"],
                street_address=street_address,
                city=addr.city,
                state=addr.state,
                zip_postal=addr.postcode,
                country_code=addr.country,
                phone=phone,
                locator_domain=locator_domain,
            )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
