from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sgscrape.sgpostal import parse_address_intl
import re
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("shopterrain")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


def fetch_data():
    locator_domain = "https://www.shopterrain.com/"
    base_url = "https://www.shopterrain.com/store_locations"
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        locations = soup.select("ol.store-results__list li.store-results__list-item")
        logger.info(f"{len(locations)} found")
        for _ in locations:
            page_url = locator_domain + _.h3.a["href"]
            logger.info(page_url)
            sp1 = bs(session.get(page_url, headers=_headers).text, "lxml")
            addr = parse_address_intl(
                " ".join(_.select_one(".store__detail--address").stripped_strings)
            )
            hours = []
            _hour = sp1.find("h3", string=re.compile(r"IN STORE"))
            if _hour:
                block = list(_hour.next_siblings)
                for x, hh in enumerate(block):
                    if not hh.string:
                        if not block[x + 1].string or (
                            block[x + 1].string and block[x + 1].string.strip()
                        ):
                            break
                        continue
                    hours.append(hh.string.strip().replace("–", "-"))
            else:
                _hour = sp1.find("h6", string=re.compile(r"Hours"))
                hours = list(_hour.find_next_sibling().stripped_strings)
            yield SgRecord(
                page_url=page_url,
                location_name=_.h3.text.strip(),
                street_address=addr.street_address_1,
                city=addr.city,
                state=addr.state,
                zip_postal=addr.postcode,
                country_code="US",
                phone=_.select_one(".store__detail--phone").text.strip(),
                hours_of_operation="; ".join(hours),
                locator_domain=locator_domain,
            )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
