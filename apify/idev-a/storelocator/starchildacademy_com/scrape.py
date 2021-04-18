from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sgselenium import SgChrome
import re
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("starchildacademy")

_headers = {
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "accept-encoding": "gzip, deflate, br",
    "accept-language": "en-US,en;q=0.9,ko;q=0.8",
    "cookie": "dm_timezone_offset=420; dm_last_visit=1618758412034; dm_total_visits=1; _ga=GA1.2.674765216.1618758415; _gid=GA1.2.536998597.1618758415; dm_last_page_view=1618760226074; dm_this_page_view=1618760232265; _sp_id.fb91=c231ab45806730e3.1618758414.1.1618760232.1618758414; _sp_ses.fb91=1618762032293",
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


def fetch_data():
    locator_domain = "https://www.starchildacademy.com"
    base_url = "https://www.starchildacademy.com/locations"
    with SgChrome() as driver:
        driver.get(base_url)
        soup = bs(driver.page_source, "lxml")
        links = soup.select(
            "div.dmRespColsWrapper .dmRespCol.small-12.medium-12.large-12 a.dmButtonLink"
        )[:-2]
        logger.info(f"{len(links)} found")
        with SgRequests() as session:
            for link in links:
                page_url = locator_domain + link["href"]
                logger.info(page_url)
                sp1 = bs(session.get(page_url, headers=_headers).text, "lxml")
                block = list(sp1.select_one("div.dmNewParagraph div").stripped_strings)
                yield SgRecord(
                    page_url=page_url,
                    location_name=block[0],
                    street_address=block[1],
                    city=block[2].split(",")[0].strip(),
                    state=block[2].split(",")[1].strip().split(" ")[0].strip(),
                    latitude=sp1.select_one("div.inlineMap")["lat"],
                    longitude=sp1.select_one("div.inlineMap")["lon"],
                    zip_postal=block[2].split(",")[1].strip().split(" ")[-1].strip(),
                    country_code="US",
                    phone=sp1.find("a", href=re.compile(r"tel:"))["phone"],
                    locator_domain=locator_domain,
                )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
