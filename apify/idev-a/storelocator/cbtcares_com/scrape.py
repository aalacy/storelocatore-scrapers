from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
import re
from sgscrape.sgpostal import parse_address_intl

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


def fetch_data():
    locator_domain = "https://www.cbtcares.com/"
    base_url = "https://www.cbtcares.com/locations/"
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        locations = soup.select("div.main-content div.grid-item")
        for _ in locations:
            addr = parse_address_intl(
                " ".join(
                    [
                        aa.text.strip()
                        for aa in _.find(
                            "strong", string=re.compile(r"Address")
                        ).find_next_siblings()
                        if aa.text.strip()
                    ][-2:]
                )
            )
            street_address = addr.street_address_1
            if addr.street_address_2:
                street_address += " " + addr.street_address_2

            _phone = _.find("a", href=re.compile(r"tel:"))
            yield SgRecord(
                page_url=base_url,
                location_name=_.h3.text.strip(),
                street_address=street_address,
                city=addr.city,
                state=addr.state,
                zip_postal=addr.postcode,
                country_code="US",
                phone=_phone.text.strip() if _phone else "",
                locator_domain=locator_domain,
                latitude=_.select_one("div.inner_location")["data-lat"],
                longitude=_.select_one("div.inner_location")["data-lng"],
                hours_of_operation="; ".join(
                    [
                        hh.text
                        for hh in _.select("div.location_hours_space")
                        if hh.text.strip()
                    ]
                ).replace("–", "-"),
            )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
