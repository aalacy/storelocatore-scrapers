from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sglogging import SgLogSetup
import re

logger = SgLogSetup().get_logger("elchico")

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}


def fetch_data():
    locator_domain = "https://www.elchico.com"
    base_url = "https://www.elchico.com/locations/"
    with SgRequests() as session:
        soup = bs(session.get(base_url).text, "lxml")
        locations = soup.select("div.wpb_wrapper a.state-child")
        logger.info(f"{len(locations)} found")
        for link in locations:
            page_url = link["href"]
            if "dhabi" in page_url:
                continue
            sp1 = bs(session.get(page_url).text, "lxml")
            _addr = list(sp1.select_one("div.address-header-up").stripped_strings)
            if "UAE" in "".join(_addr):
                continue
            logger.info(page_url)
            hours = []
            temp = list(sp1.select_one("div.hrs-header-up p").stripped_strings)
            for x in range(0, len(temp), 2):
                hours.append(f"{temp[x]} {temp[x+1]}")
            coord = (
                sp1.find("div", string=re.compile(r"Driving Direction"))
                .find_parent()["href"]
                .split("/")[-1]
                .split(",")
            )
            yield SgRecord(
                page_url=page_url,
                location_name=sp1.select_one("div.title-up").text.strip(),
                street_address=_addr[0],
                city=_addr[-1].split(",")[0].strip(),
                state=_addr[-1].split(",")[1].strip().split(" ")[0].strip(),
                zip_postal=_addr[-1].split(",")[1].strip().split(" ")[-1].strip(),
                phone=sp1.select_one("div.tel-header-up").text.strip(),
                latitude=coord[0],
                longitude=coord[1],
                country_code="US",
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours).replace("–", "-"),
            )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
