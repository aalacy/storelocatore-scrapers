from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests
from sgscrape.sgpostal import parse_address_intl
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("mycarecompass")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


def fetch_data():
    locator_domain = "https://www.cantinalaredo.com/"
    base_url = "https://www.cantinalaredo.com/locations/"
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        locations = soup.select("div.wpb_wrapper div.single-location")
        logger.info(f"{len(locations)} found")
        for location in locations:
            page_url = location.select_one(".location-visit a")["href"]
            logger.info(page_url)
            location_name = " ".join(
                [_ for _ in location.select_one(".location-name").stripped_strings]
            )
            if "UAE" in location_name:
                continue
            addr = parse_address_intl(
                location.select_one(".location-address")
                .text.replace("Across from Gate 6", "")
                .strip()
            )
            street_address = addr.street_address_1
            if addr.street_address_2:
                street_address += " " + addr.street_address_2
            sp1 = bs(session.get(page_url, headers=_headers).text, "lxml")
            coord = sp1.select_one("div.address a")["href"].split("/")[-1].split(",")
            hours_of_operation = (
                location.select_one(".hours p")
                .text.replace("\n", ";")
                .replace("–", "-")
            )
            if "flight" in hours_of_operation or "departure" in hours_of_operation:
                hours_of_operation = ""
            yield SgRecord(
                page_url=page_url,
                location_name=location_name,
                street_address=street_address,
                city=addr.city,
                state=addr.state,
                zip_postal=addr.postcode,
                country_code="US",
                phone=location.select_one(".tel").text.strip(),
                locator_domain=locator_domain,
                latitude=coord[0],
                longitude=coord[1],
                hours_of_operation=hours_of_operation,
            )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
