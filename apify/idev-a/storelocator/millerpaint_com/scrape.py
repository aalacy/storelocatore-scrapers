from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sglogging import SgLogSetup
from sgscrape.sgpostal import parse_address_intl

logger = SgLogSetup().get_logger("millerpaint")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


def fetch_data():
    locator_domain = "https://www.millerpaint.com/"
    base_url = "https://www.millerpaint.com/stores/"
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        links = soup.select("div.uabb-masonary-cat-41")
        logger.info(f"{len(links)} found")
        for link in links:
            page_url = link.a["href"]
            logger.info(page_url)
            sp1 = bs(session.get(page_url, headers=_headers).text, "lxml")
            coord = (
                sp1.select_one("div.fl-html iframe")["data-src"]
                .split("!2d")[1]
                .split("!2m")[0]
                .split("!3d")
            )
            _addr = list(sp1.select_one("div.fl-rich-text h4").stripped_strings)
            addr = parse_address_intl(_addr[0])
            street_address = addr.street_address_1
            if addr.street_address_2:
                street_address += " " + addr.street_address_2
            yield SgRecord(
                page_url=page_url,
                raw_address=_addr[0],
                location_name=sp1.select_one("div.fl-rich-text h2")
                .text.strip()
                .replace("–", "-"),
                street_address=street_address,
                city=addr.city,
                state=addr.state,
                zip_postal=addr.postcode,
                country_code="US",
                phone=_addr[-1].split(":")[-1].replace("Phone", ""),
                locator_domain=locator_domain,
                latitude=coord[1],
                longitude=coord[0],
                hours_of_operation="; ".join(
                    sp1.select_one("div.fl-rich-text p").stripped_strings
                ).replace("–", "-"),
            )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
