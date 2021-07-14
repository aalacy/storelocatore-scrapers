from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("avondalestores")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


def fetch_data():
    locator_domain = "https://www.avondalestores.com"
    base_url = "https://www.avondalestores.com/site/location-listing"
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        locations = soup.select("ul.cmsi-showcase-list li")
        logger.info(f"{len(locations)} found")
        for _ in locations:
            page_url = locator_domain + _.a["href"]
            logger.info(page_url)
            sp1 = bs(session.get(page_url, headers=_headers).text, "lxml")
            addr = list(sp1.select_one("div.primary p").stripped_strings)
            yield SgRecord(
                page_url=page_url,
                location_name=_.h3.a.text.split("|")[-1],
                store_number=_.h3.a.text.split("|")[0].split("#")[-1].strip(),
                street_address=addr[0].strip(),
                city=addr[1].split(",")[0].strip(),
                state=addr[1].split(",")[1].strip(),
                country_code="CA",
                phone=addr[-1].replace("(Pizzeria)", ""),
                locator_domain=locator_domain,
            )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
