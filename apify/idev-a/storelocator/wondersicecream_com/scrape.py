from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sglogging import SgLogSetup
from sgscrape.sgpostal import parse_address_intl

logger = SgLogSetup().get_logger("wondersicecream")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


def fetch_data():
    locator_domain = "https://wondersicecream.com/"
    base_url = (
        "https://wondersicecream.com/wonders-rolled-ice-cream-franchise-locations/"
    )
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        links = soup.select(
            "main section .elementor-element-populated .elementor-widget-wrap"
        )
        logger.info(f"{len(links)} found")
        for link in links:
            if not link.h3 and not link.p:
                continue
            if "coming" in link.p.text.lower():
                break
            addr = parse_address_intl(list(link.p.stripped_strings)[1])
            street_address = addr.street_address_1
            if addr.street_address_2:
                street_address += " " + addr.street_address_2
            phone = ""
            if link.a:
                phone = link.a.text
            yield SgRecord(
                page_url=base_url,
                location_name=link.h3.text.strip(),
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
