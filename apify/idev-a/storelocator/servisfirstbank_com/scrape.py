from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sglogging import SgLogSetup
import re
from sgscrape.sgpostal import parse_address_intl

logger = SgLogSetup().get_logger("servisfirstbank")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


def fetch_data():
    locator_domain = "https://www.servisfirstbank.com"
    base_url = "https://www.servisfirstbank.com/locations/"
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        links = soup.select("div#locations_squares > a")
        logger.info(f"{len(links)} found")
        for link in links:
            page_url = locator_domain + link["href"]
            logger.info(page_url)
            sp1 = bs(session.get(page_url, headers=_headers).text, "lxml")
            for _ in sp1.select("div#location_spots > div"):
                if not _.text.strip():
                    continue
                addr = parse_address_intl(
                    " ".join(_.select_one(".spot_text").stripped_strings)
                )
                street_address = addr.street_address_1
                if addr.street_address_2:
                    street_address += " " + addr.street_address_2
                _hr = _.find("div", string=re.compile(r"Lobby Hours"))
                hours = []
                if _hr:
                    hours = " ".join(list(_hr.find_next_sibling().stripped_strings))
                location_type = "branch"
                if _.select_one('img[alt="atm icon"]'):
                    location_type += ",atm"
                phone = ""
                if _.find("a", href=re.compile(r"tel:")):
                    phone = _.find("a", href=re.compile(r"tel:")).text.strip()
                yield SgRecord(
                    page_url=page_url,
                    location_name=_.select_one("div.spot_title").text.strip(),
                    street_address=street_address,
                    city=addr.city,
                    state=addr.state,
                    zip_postal=addr.postcode,
                    country_code="US",
                    phone=phone,
                    locator_domain=locator_domain,
                    location_type=location_type,
                    hours_of_operation=hours.replace("–", "-"),
                )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
