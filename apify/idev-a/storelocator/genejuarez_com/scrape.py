from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sglogging import SgLogSetup
import re
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

logger = SgLogSetup().get_logger("genejuarez")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


def fetch_data():
    locator_domain = "https://www.genejuarez.com"
    base_url = "https://www.genejuarez.com/locations/"
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        links = soup.select("div.location-item")
        logger.info(f"{len(links)} found")
        for link in links:
            page_url = (
                locator_domain + link.select_one("div.location-item-link-1 a")["href"]
            )
            logger.info(page_url)
            sp1 = bs(session.get(page_url, headers=_headers).text, "lxml")
            coord = (
                sp1.select_one("div.details-address-link a")["href"]
                .split("/@")[1]
                .split("/data")[0]
                .split(",")
            )
            addr = list(
                link.select_one(".location-item-top-address p").stripped_strings
            )
            hours = [
                " ".join(hh.stripped_strings)
                for hh in link.select("ul.location-hours li")
            ]
            yield SgRecord(
                page_url=page_url,
                location_name=link.h3.text.strip(),
                street_address=" ".join(addr[:-1]),
                city=addr[-1].split(",")[0].strip(),
                state=addr[-1].split(",")[1].strip().split(" ")[0].strip(),
                zip_postal=addr[-1].split(",")[1].strip().split(" ")[-1].strip(),
                country_code="US",
                phone=link.find("a", href=re.compile(r"tel:"))
                .text.replace("Call or text", "")
                .strip(),
                locator_domain=locator_domain,
                latitude=coord[0],
                longitude=coord[1],
                hours_of_operation="; ".join(hours).replace("–", "-"),
                raw_address=" ".join(addr),
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
