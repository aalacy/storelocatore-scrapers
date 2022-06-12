from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sglogging import SgLogSetup
from sgscrape.sgpostal import parse_address_intl

logger = SgLogSetup().get_logger("renodepot")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


def fetch_data():
    locator_domain = "https://www.renodepot.com/"
    base_url = "https://www.renodepot.com/en/find-a-warehouse"
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        links = soup.select("div.locator-container a")
        logger.info(f"{len(links)} found")
        for link in links:
            page_url = link["href"]
            logger.info(page_url)
            sp1 = bs(session.get(page_url, headers=_headers).text, "lxml")
            addr = parse_address_intl(
                sp1.select_one(".details-map__info-address a").text.strip()
            )
            street_address = addr.street_address_1
            if addr.street_address_2:
                street_address += " " + addr.street_address_2
            hours = [
                ": ".join(hh.stripped_strings)
                for hh in sp1.select("div.opening-hours.opening-hours-store tr")
            ]
            yield SgRecord(
                page_url=page_url,
                location_name=sp1.select_one("div.details-map__info h2").text.strip(),
                street_address=street_address,
                city=addr.city,
                state=addr.state,
                zip_postal=addr.postcode,
                country_code="CA",
                phone=sp1.select_one(".details-map__info-phone").text.strip(),
                locator_domain=locator_domain,
                latitude=sp1.select_one('meta[itemprop="latitude"]')["content"],
                longitude=sp1.select_one('meta[itemprop="longitude"]')["content"],
                hours_of_operation="; ".join(hours).replace("–", "-"),
            )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
