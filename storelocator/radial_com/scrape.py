from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sglogging import SgLogSetup
import re
from sgscrape.sgpostal import parse_address_intl

logger = SgLogSetup().get_logger("radial")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


def fetch_data():
    locator_domain = "https://www.radial.com/"
    base_url = "https://www.radial.com/about/locations"
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        rows = soup.find(
            "h3", string=re.compile(r"Fulfillment Centers")
        ).find_next_siblings("div", recursive=False)
        logger.info(f"{len(rows)} found")
        for row in rows:
            locations = row.select("div.col-sm-6")
            for _ in locations:
                if not _.text.strip():
                    continue
                state = _.h4.text.strip() if _.h4 else ""
                _addr = list(_.stripped_strings)
                if state and _addr[0] == state:
                    del _addr[0]
                addr = parse_address_intl(" ".join(_addr))
                street_address = addr.street_address_1
                if addr.street_address_2:
                    street_address += " " + addr.street_address_2
                yield SgRecord(
                    page_url=base_url,
                    raw_address=" ".join(_addr),
                    location_name=street_address,
                    street_address=street_address,
                    city=addr.city,
                    state=addr.state,
                    zip_postal=addr.postcode,
                    location_type="fulfillment centers",
                    country_code=addr.country,
                    locator_domain=locator_domain,
                )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
