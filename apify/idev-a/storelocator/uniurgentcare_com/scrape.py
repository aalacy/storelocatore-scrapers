from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sglogging import SgLogSetup
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
import re

logger = SgLogSetup().get_logger("uniurgentcare")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


def fetch_data():
    locator_domain = "https://uniurgentcare.com/"
    base_url = "https://uniurgentcare.com/locations/"
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        locations = (
            soup.find("a", string=re.compile(r"^Locations"))
            .find_next_sibling()
            .select("a")
        )
        logger.info(f"{len(locations)} found")
        for _ in locations:
            page_url = _["href"]
            logger.info(page_url)
            sp1 = bs(session.get(page_url, headers=_headers).text, "lxml")
            map_a = sp1.find("a", href=re.compile(r"/maps"))
            addr = list(map_a.find_parent().stripped_strings)
            hours = list(sp1.select("div.entry-content p")[-1].stripped_strings)[1:]
            try:
                coord = map_a["href"].split("&sll=")[1].split("&")[0].split(",")
            except:
                try:
                    coord = map_a["href"].split("/@")[1].split("/data")[0].split(",")
                except:
                    coord = ["", ""]

            phone = ""
            if sp1.select_one("p.location-telephone"):
                phone = sp1.select_one("p.location-telephone").text.strip()
            elif sp1.find("a", href=re.compile(r"tel")):
                phone = sp1.find("a", href=re.compile(r"tel")).text.strip()

            yield SgRecord(
                page_url=page_url,
                location_name=_.text.strip().replace("–", "-"),
                street_address=" ".join(addr[:-1]),
                city=addr[-1].split(",")[0].strip(),
                state=addr[-1].split(",")[1].strip().split(" ")[0].strip(),
                zip_postal=addr[-1].split(",")[1].strip().split(" ")[-1].strip(),
                country_code="US",
                phone=phone,
                locator_domain=locator_domain,
                latitude=coord[0],
                longitude=coord[1],
                hours_of_operation="; ".join(hours).replace("–", "-"),
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
