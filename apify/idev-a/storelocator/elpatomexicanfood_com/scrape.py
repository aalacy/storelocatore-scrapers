from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sglogging import SgLogSetup
import re

logger = SgLogSetup().get_logger("nxcli")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://50908c389b.nxcli.net"
base_url = "https://50908c389b.nxcli.net/locations/"


def fetch_data():
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        links = soup.select("div.et_pb_row div.et_pb_main_blurb_image a")
        logger.info(f"{len(links)} found")
        for link in links:
            page_url = link["href"]
            logger.info(page_url)
            sp1 = bs(session.get(page_url, headers=_headers).text, "lxml")
            block = list(
                sp1.select_one("div.et_pb_text_align_center h1").stripped_strings
            )
            addr = block[0].split("•")
            hours = []
            _hr = sp1.find("", string=re.compile(r"Hours of Operation:"))
            if _hr:
                hours = list(_hr.find_parent().stripped_strings)[1:]
            try:
                coord = (
                    sp1.select_one("div.et_pb_code_inner iframe")["src"]
                    .split("!2d")[1]
                    .split("!2d")[0]
                    .split("!3d")
                )
            except:
                coord = ["", ""]
            if not addr[1]:
                continue
            yield SgRecord(
                page_url=page_url,
                location_name=sp1.h1.text.strip(),
                street_address=addr[0],
                city=addr[1].split(",")[0].strip(),
                state=addr[1].split(",")[1].strip().split(" ")[0].strip(),
                zip_postal=addr[1].split(",")[1].strip().split(" ")[-1].strip(),
                country_code="US",
                phone=block[1],
                locator_domain=locator_domain,
                latitude=coord[1],
                longitude=coord[0],
                hours_of_operation="; ".join(hours).replace("–", "-"),
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
