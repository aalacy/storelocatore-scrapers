from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgselenium import SgChrome
from bs4 import BeautifulSoup as bs
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("salsafrescagrill")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


def fetch_data():
    locator_domain = "https://www.salsafrescagrill.com/"
    base_url = "https://www.salsafrescagrill.com/locations"
    with SgChrome() as driver:
        driver.get(base_url)
        soup = bs(driver.page_source, "lxml")
        links = [
            aa
            for aa in soup.find_all("a")
            if aa.get("aria-label", "").endswith("locations")
        ]
        logger.info(f"{len(links)} found")
        for link in links:
            logger.info(link["href"])
            driver.get(link["href"])
            sp1 = bs(driver.page_source, "lxml")
            locs = sp1.select(
                'main#PAGES_CONTAINER div[data-testid="mesh-container-content"] > div[data-testid="richTextElement"]'
            )
            locations = []
            for loc in locs:
                if loc.h2 and loc.h2.text.strip() not in ["Connecticut", "NOW OPEN"]:
                    locations.append(loc)
            logger.info(f"{len(locations)} found")
            for loc in locations:
                block = list(loc.stripped_strings)
                yield SgRecord(
                    page_url=link["href"],
                    location_name=block[0],
                    street_address=block[0],
                    city=block[1].split(",")[0],
                    state=block[1].split(",")[1],
                    country_code="US",
                    locator_domain=locator_domain,
                    phone=block[2],
                )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
