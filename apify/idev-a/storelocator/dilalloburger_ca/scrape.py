from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sglogging import SgLogSetup
from sgscrape.sgpostal import parse_address_intl

logger = SgLogSetup().get_logger("dilalloburger")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


def fetch_data():
    locator_domain = "https://www.dilalloburger.ca/"
    base_url = "https://www.dilalloburger.ca/locations/"
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        locations = soup.select("div.wpb_row.row-inner")[1].select("div.wpb_column")
        logger.info(f"{len(locations)} found")
        names = [_.text.strip() for _ in soup.select("div.menu-bloginfo p strong")]
        logger.info(f"{len(names)} found")
        for x, _ in enumerate(locations):
            addr = parse_address_intl(
                " ".join(_.select_one(".text-top-reduced p").stripped_strings)
            )
            street_address = addr.street_address_1
            if addr.street_address_2:
                street_address += " " + addr.street_address_2
            coord = (
                _.select_one(".btn-container a")["href"]
                .split("/@")[1]
                .split("z/data")[0]
                .split(",")
            )
            location_name = names[x]
            if location_name.endswith(":"):
                location_name = location_name[:-1]
            yield SgRecord(
                page_url=base_url,
                location_name=location_name,
                street_address=street_address,
                city=addr.city,
                state=addr.state,
                zip_postal=addr.postcode,
                country_code="CA",
                phone=_.h2.text.strip(),
                locator_domain=locator_domain,
                latitude=coord[0],
                longitude=coord[1],
            )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
