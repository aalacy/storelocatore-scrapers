from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sglogging import SgLogSetup
from sgscrape.sgpostal import parse_address_intl

logger = SgLogSetup().get_logger("cupsfrozenyogurt")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


def fetch_data():
    locator_domain = "https://www.cupsfrozenyogurt.com/"
    base_url = "https://www.cupsfrozenyogurt.com/locations/"
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        links = soup.select("div.stores .vc_column_container")
        logger.info(f"{len(links)} found")
        for x in range(0, len(links), 2):
            _ = links[x]
            if not _.text.strip():
                break
            _addr = list(_.p.stripped_strings)
            addr = parse_address_intl(" ".join(_addr[:-1]))
            street_address = addr.street_address_1
            if addr.street_address_2:
                street_address += " " + addr.street_address_2
            hours = list(_.select("p")[1].stripped_strings)[1:]
            coord = (
                links[x + 1]
                .iframe["src"]
                .split("!2d")[1]
                .split("!2m")[0]
                .split("!3m")[0]
                .split("!3d")
            )
            yield SgRecord(
                page_url=base_url,
                location_name=_.h3.text.strip(),
                street_address=street_address,
                city=addr.city,
                state=addr.state,
                zip_postal=addr.postcode,
                country_code="US",
                phone=_addr[-1],
                locator_domain=locator_domain,
                latitude=coord[1],
                longitude=coord[0],
                hours_of_operation="; ".join(hours).replace("–", "-"),
            )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
