from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sglogging import SgLogSetup
from sgscrape.sgpostal import parse_address_intl

logger = SgLogSetup().get_logger("caringseniorservice")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


def fetch_data():
    locator_domain = "https://www.caringseniorservice.com/"
    base_url = "https://www.caringseniorservice.com/locations"
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        links = soup.select("div.locations-section div.item")
        logger.info(f"{len(links)} found")
        for link in links:
            page_url = link.select_one(".location-title").a["href"]
            _addr = list(link.select_one(".location").stripped_strings)
            addr = parse_address_intl(" ".join(_addr[:-1]))
            street_address = addr.street_address_1
            if addr.street_address_2:
                street_address += " " + addr.street_address_2
            try:
                coord = (
                    link.select_one("div.button-wrapper a")["href"]
                    .split("!1d")[1]
                    .split("!2d")
                )
            except:
                coord = ["", ""]
            try:
                yield SgRecord(
                    page_url=page_url,
                    location_name=link.select_one(".location-title").text.strip(),
                    street_address=street_address,
                    city=addr.city,
                    state=addr.state,
                    zip_postal=addr.postcode,
                    country_code="US",
                    phone=_addr[-1],
                    locator_domain=locator_domain,
                    latitude=coord[1],
                    longitude=coord[0],
                )
            except:
                import pdb

                pdb.set_trace()


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
