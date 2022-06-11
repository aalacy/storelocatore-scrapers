from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sglogging import SgLogSetup
from sgscrape.sgpostal import parse_address_intl
import re

logger = SgLogSetup().get_logger("graffitijunktion")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


def fetch_data():
    locator_domain = "https://graffitijunktion.com/"
    base_url = "https://graffitijunktion.com/locations/"
    streets = []
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        locations = soup.select("div#post-521 > .vc_row")[1].select(
            ".vc_row > .wpb_column"
        )
        logger.info(f"{len(locations)} found")
        for _ in locations:
            if not _.p:
                logger.info("skip")
                continue
            block = list(_.p.stripped_strings)
            addr = parse_address_intl(block[1])
            street_address = addr.street_address_1
            if addr.street_address_2:
                street_address += " " + addr.street_address_2
            if street_address in streets:
                continue
            streets.append(street_address)
            hours = []
            _hr = _.find("h6", string=re.compile(r"Hours"))
            if _hr:
                temp = list(_hr.find_next_sibling().stripped_strings)
                for x in range(0, len(temp), 2):
                    hours.append(f"{temp[x]} {temp[x+1]}")
            yield SgRecord(
                page_url=base_url,
                location_name=_.h2.text.strip(),
                street_address=street_address,
                city=addr.city,
                state=addr.state,
                zip_postal=addr.postcode,
                country_code="US",
                phone=block[-1],
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours).replace("–", "-"),
            )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
