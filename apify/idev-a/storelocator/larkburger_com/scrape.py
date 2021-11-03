from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sglogging import SgLogSetup
import re
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

logger = SgLogSetup().get_logger("larkburger")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


def fetch_data():
    locator_domain = "https://larkburger.com/"
    base_url = "https://larkburger.com/locations/"
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        locations = soup.select("div.locations-list .block")
        logger.info(f"{len(locations)} found")
        for _ in locations:
            page_url = _.find("a", string=re.compile(r"View Details"))["href"]
            addr = _.address.text.strip().split("\r\n")
            hours = list(_.select_one(".hours").stripped_strings)[1:]
            coord = (
                _.find("a", string=re.compile(r"Get Directions"))["href"]
                .split("/@")[1]
                .split(",")
            )
            phone = ""
            if _.select_one("div.phone"):
                phone = _.select_one("div.phone").text.strip()
            yield SgRecord(
                page_url=page_url,
                location_name=_.h3.text.strip().replace("–", "-"),
                street_address=addr[0],
                city=addr[1].split(",")[0].strip(),
                state=addr[1].split(",")[1].strip().split(" ")[0].strip(),
                zip_postal=addr[1].split(",")[1].strip().split(" ")[-1].strip(),
                country_code="US",
                phone=phone,
                locator_domain=locator_domain,
                latitude=coord[0],
                longitude=coord[1],
                hours_of_operation="; ".join(hours)
                .replace(",", "")
                .replace("\r", " ")
                .replace("–", "-")
                .replace("\n", "; "),
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
