from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sglogging import SgLogSetup
from sgscrape.sgpostal import parse_address_intl

logger = SgLogSetup().get_logger("salsafrescagrill")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


def fetch_data():
    locator_domain = "https://www.salsafrescagrill.com/"
    base_url = "https://www.salsafrescagrill.com/locations"
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        links = [
            aa
            for aa in soup.find_all("a")
            if aa.get("aria-label", "").endswith("locations")
        ]
        for link in links:
            logger.info(link["href"])
            sp1 = bs(session.get(link["href"], headers=_headers).text, "lxml")
            locs = sp1.select(
                'div[data-mesh-id="comp-kbgjwzaiinlineContent-gridContainer"] div[data-testid="richTextElement"]'
            )
            for x, loc in enumerate(locs):
                if not loc.select_one("h2"):
                    del locs[x]
            for x in range(0, len(locs), 3):
                addr = parse_address_intl(locs[x] + " " + locs[x + 1])
                yield SgRecord(
                    page_url=link["href"],
                    location_name=locs[0],
                    street_address=locs[0],
                    city=addr.city,
                    state=addr.state,
                    zip_postal=addr.postcode,
                    country_code="US",
                    locator_domain=locator_domain,
                    phone=locs[x + 1],
                )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
