from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sglogging import SgLogSetup
import re

logger = SgLogSetup().get_logger("cabreras")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.cabreras.com"
base_url = "https://www.cabreras.com/locations"


def fetch_data():
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        locations = soup.select('a[data-testid="linkElement"]')
        for link in locations:
            if "-location" not in link["href"]:
                continue
            page_url = link["href"]
            sp1 = bs(session.get(page_url, headers=_headers).text, "lxml")
            addr = [
                aa.text.strip()
                for aa in sp1.find("span", string=re.compile(r"^Address:"))
                .find_parent("h2")
                .find_next_siblings("h2")
            ]
            hours = [
                hh.text.strip()
                for hh in sp1.find("span", string=re.compile(r"^Hours"))
                .find_parent("h2")
                .find_next_siblings("p")
            ]
            zip_postal = addr[-1].split(",")[1].strip().split(" ")[-1].strip()
            href = sp1.find("a", href=re.compile(r"https://www\.google\.com/maps"))[
                "href"
            ]
            if zip_postal in href:
                coord = href.split("@")[1].split(",")
            else:
                coord = ("", "")
            yield SgRecord(
                page_url=page_url,
                location_name=sp1.select_one("main h1").text.strip(),
                street_address=" ".join(addr[:-1]),
                city=addr[-1].split(",")[0].strip(),
                state=addr[-1].split(",")[1].strip().split(" ")[0].strip(),
                zip_postal=zip_postal,
                country_code="US",
                phone=sp1.find("span", string=re.compile(r"Call Ahead"))
                .find_parent("h2")
                .find_next_sibling("h2")
                .text.strip(),
                latitude=coord[0],
                longitude=coord[1],
                hours_of_operation="; ".join(hours),
                locator_domain=locator_domain,
                raw_address=" ".join(addr),
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
