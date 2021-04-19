from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sgselenium import SgChrome
import re
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("linsgrocery")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


def fetch_data():
    locator_domain = "https://linsgrocery.com"
    base_url = "https://linsgrocery.com/"
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        links = soup.select("div.footerSection")[1].select("a")
        logger.info(f"{len(links)} found")
        with SgChrome() as driver:
            for link in links:
                page_url = locator_domain + link["href"]
                logger.info(page_url)
                driver.get(page_url)
                sp1 = bs(driver.page_source, "lxml")
                hour_block = sp1.find("h5", string=re.compile(r"Store Hours"))
                hours_of_operation = " ".join(
                    hour_block.find_next_sibling("p").stripped_strings
                )
                addr = list(
                    sp1.find("h5", string=re.compile(r"Store Address"))
                    .find_next_sibling("p")
                    .stripped_strings
                )
                coord = (
                    sp1.select_one("div#map-container-single")
                    .iframe["src"]
                    .split("!2d")[1]
                    .split("!3m")[0]
                    .split("!3d")
                )
                yield SgRecord(
                    page_url=page_url,
                    location_name=sp1.select_one("span#theStoreName").text,
                    street_address=addr[0],
                    city=addr[1].split(",")[0].strip(),
                    state=addr[1].split(",")[1].strip().split(" ")[0].strip(),
                    zip_postal=addr[1].split(",")[1].strip().split(" ")[-1].strip(),
                    latitude=coord[1],
                    longitude=coord[0],
                    country_code="US",
                    locator_domain=locator_domain,
                    phone=sp1.find("a", href=re.compile(r"tel:")).text,
                    hours_of_operation=hours_of_operation,
                )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
