from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("bestfitnessgyms")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


def fetch_data():
    locator_domain = "https://bestfitnessgyms.com"
    base_url = "https://bestfitnessgyms.com/locations/"
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        links = soup.select("div.location_group ul li a")
        for link in links:
            page_url = locator_domain + link["href"]
            logger.info(page_url)
            sp1 = bs(session.get(page_url, headers=_headers).text, "lxml")
            yield SgRecord(
                page_url=page_url,
                location_name=sp1.select_one("div.site_fvcard span.h3").text.strip(),
                street_address=sp1.select_one("span.adr .street-address").text,
                city=sp1.select_one("span.adr .locality").text,
                state=sp1.select_one("span.adr .region").text,
                zip_postal=sp1.select_one("span.adr .postal-code").text,
                country_code="US",
                phone=sp1.select_one("span.tel a").text,
                locator_domain=locator_domain,
            )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
