from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("coldstorage")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "http://www.coldstorage.com"
base_url = "http://www.coldstorage.com/locations/"


def fetch_data():
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        links = soup.select("div.location-wrap")
        logger.info(f"{len(links)} found")
        for link in links:
            addr = link.a.text.strip().split(",")
            location_name = link.strong.text.strip()
            yield SgRecord(
                page_url=base_url,
                location_name=location_name,
                street_address=addr[0],
                city=location_name.split(",")[0].strip(),
                state=location_name.split(",")[1].strip(),
                zip_postal=addr[1],
                country_code="CA",
                locator_domain=locator_domain,
            )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
