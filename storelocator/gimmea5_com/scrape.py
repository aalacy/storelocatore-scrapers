from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sglogging import SgLogSetup
from sgscrape.sgpostal import parse_address_intl
import re

logger = SgLogSetup().get_logger("gimmea5")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


def fetch_data():
    locator_domain = "https://gimmea5.com/"
    base_url = "https://gimmea5.com/locations/"
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        locations = soup.select(
            ".wpb_row.vc_inner.vc_row.vc_row-fluid .wpb_wrapper .mk-text-block"
        )
        logger.info(f"{len(locations)} found")
        for _ in locations:
            block = list(_.stripped_strings)
            _addr = block[1:-1]
            if "phone" in _addr[-1].lower():
                del _addr[-1]
            addr = parse_address_intl(" ".join(_addr))
            street_address = addr.street_address_1
            if addr.street_address_2:
                street_address += " " + addr.street_address_2
            phone = (
                _.find("a", href=re.compile(r"tel:"))
                .text.split(":")[-1]
                .replace("Phone", "")
                .strip()
            )
            if not phone:
                phone = _.find("span", {"role": "link"}).text
            yield SgRecord(
                page_url=base_url,
                location_name=block[0],
                street_address=street_address,
                city=addr.city,
                state=addr.state,
                zip_postal=addr.postcode,
                country_code="US",
                phone=phone,
                locator_domain=locator_domain,
            )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
