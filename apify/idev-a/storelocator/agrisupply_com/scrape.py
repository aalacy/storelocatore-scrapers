from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sglogging import SgLogSetup
import re

logger = SgLogSetup().get_logger("agrisupply")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


def fetch_data():
    locator_domain = "https://www.agrisupply.com"
    base_url = "https://www.agrisupply.com/retail-store-locations/a/80/"
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        links = soup.select("div.container div.col-md-4 div.card a")
        logger.info(f"{len(links)} found")
        for link in links:
            page_url = locator_domain + link["href"]
            logger.info(page_url)
            sp1 = bs(session.get(page_url, headers=_headers).text, "lxml")
            _hr = sp1.find("div", string=re.compile(r"^Hours"))
            if _hr:
                hours = [
                    " ".join(hh.stripped_strings)
                    for hh in _hr.find_next_sibling().select("p.card-text")
                ]
            coord = (
                sp1.select_one("iframe.google-map")["src"]
                .split("&ll=")[1]
                .split("&")[0]
                .split(",")
            )
            yield SgRecord(
                page_url=page_url,
                location_name=link.strong.text.strip(),
                street_address=sp1.select_one(
                    'span[itemprop="streetAddress"]'
                ).text.strip(),
                city=sp1.select_one('span[itemprop="addressLocality"]').text.strip(),
                state=sp1.select_one('span[itemprop="addressRegion"]').text.strip(),
                zip_postal=sp1.select_one('span[itemprop="postalCode"]').text.strip(),
                country_code="US",
                phone=sp1.select_one('p[itemprop="telephone"] a').text.strip(),
                locator_domain=locator_domain,
                latitude=coord[0],
                longitude=coord[1],
                hours_of_operation="; ".join(hours).replace("–", "-"),
            )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
