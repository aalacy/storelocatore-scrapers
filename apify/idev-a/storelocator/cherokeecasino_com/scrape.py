from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sglogging import SgLogSetup
from sgscrape.sgpostal import parse_address_intl

logger = SgLogSetup().get_logger("cherokeecasino")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


def fetch_data():
    locator_domain = "https://cherokeecasino.com"
    base_url = "https://cherokeecasino.com/"
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        links = soup.select_one("footer .nav-links").select("li a")
        logger.info(f"{len(links)} found")
        for link in links:
            page_url = link["href"].replace(":443", "")
            if not page_url.startswith("https"):
                page_url = locator_domain + page_url
            logger.info(page_url)
            sp1 = bs(session.get(page_url, headers=_headers).text, "lxml")
            block = list(
                sp1.select_one(
                    "section.promo-card-container .promo-card-container__floating-card"
                ).stripped_strings
            )[1:-1]
            addr = parse_address_intl(block[2])
            coord = (
                sp1.select_one(
                    "section.promo-card-container .promo-card-container__floating-card"
                )
                .select("a")[-1]["href"]
                .split("destination=")[1]
                .split("%2c")
            )
            street_address = addr.street_address_1
            if addr.street_address_2:
                street_address += " " + addr.street_address_2
            yield SgRecord(
                page_url=page_url,
                location_name=block[0],
                street_address=street_address,
                city=addr.city,
                state=addr.state,
                zip_postal=addr.postcode,
                country_code="US",
                phone=block[3],
                locator_domain=locator_domain,
                latitude=coord[0],
                longitude=coord[1],
            )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
