from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgscrape.sgpostal import parse_address_intl
from bs4 import BeautifulSoup as bs
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("royalbluegrocery")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.royalbluegrocery.com"


def parse_detail(sp2, detail, page_url):
    block = sp2.select("div.blockInnerContent")[-1].select("p")
    addr = parse_address_intl(" ".join(block[0].stripped_strings))
    hours = []
    logger.info(f"[*****] {page_url}")
    if sp2.select_one("h2.pageSubtitle"):
        hours = (
            sp2.select_one("h2.pageSubtitle")
            .text.replace("!", "")
            .replace("We have reopened on Congress", "")
            .split(",")
        )
    else:
        hours = [sp2.select("div.blockInnerContent p")[1].text]
    return SgRecord(
        page_url=page_url,
        location_name=detail.text,
        street_address=addr.street_address_1,
        city=addr.city,
        state=addr.state,
        zip_postal=addr.postcode,
        country_code="US",
        locator_domain=locator_domain,
        hours_of_operation="; ".join(hours),
    )


def fetch_data():
    base_url = "https://www.royalbluegrocery.com/locations"
    with SgRequests() as session:
        sp = bs(session.get(base_url, headers=_headers).text, "lxml")
        cities = sp.select("div.itemsCollectionContent  h2 a")
        logger.info(f"[city] {len(cities)} found")
        for city in cities:
            city_url = locator_domain + city["href"]
            sp1 = bs(session.get(city_url, headers=_headers).text, "lxml")
            locations = sp1.select("div.itemsCollectionContent h2 a")
            logger.info(f"[{city.text}] {len(locations)}found")
            if locations:
                for detail in locations:
                    page_url = locator_domain + detail["href"]
                    sp2 = bs(session.get(page_url, headers=_headers).text, "lxml")
                    yield parse_detail(sp2, detail, page_url)
            else:
                yield parse_detail(sp1, city, city_url)


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
