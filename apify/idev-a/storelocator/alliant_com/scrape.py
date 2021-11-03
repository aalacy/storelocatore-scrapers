from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("alliant")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


def fetch_data():
    locator_domain = "https://www.alliant.com/"
    base_url = "https://www.alliant.com/About-Us/Pages/Office-Locations.aspx"
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        links = soup.select("div#officeListItem")
        logger.info(f"{len(links)} found")
        for link in links:
            yield SgRecord(
                page_url=base_url,
                location_name=link.select_one("a.name").text.strip(),
                street_address=link.select_one("span.streetAddress").text.strip(),
                city=link.select_one("span.city").text.strip(),
                state=link.select_one("span.state").text.strip(),
                zip_postal=link.select_one("span.postalCode").text.strip(),
                country_code="US",
                phone=link.select_one("span.telephone").text.strip(),
                locator_domain=locator_domain,
                latitude=link.select_one("span.latitude").text.strip(),
                longitude=link.select_one("span.longitude").text.strip(),
            )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
