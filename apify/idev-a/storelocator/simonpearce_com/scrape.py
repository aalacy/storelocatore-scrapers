from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sglogging import SgLogSetup
import re
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

logger = SgLogSetup().get_logger("simonpearce")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.simonpearce.com"
base_url = "https://www.simonpearce.com/our-stores"


def fetch_data():
    with SgRequests() as session:
        links = bs(session.get(base_url, headers=_headers).text, "lxml").select(
            "div.pagebuilder-column"
        )
        logger.info(f"{len(links)} found")
        for link in links:
            if not link.p or not link.strong:
                continue
            page_url = link.strong.a["href"]
            if page_url == "https://www.simonpearce.com/store-locator":
                continue
            if not page_url.startswith("https"):
                page_url = locator_domain + page_url
            logger.info(page_url)
            addr = list(link.select("p")[-1].stripped_strings)
            hours = []
            sp1 = bs(session.get(page_url, headers=_headers).text, "lxml")
            _hr = sp1.find("h3", string=re.compile(r"STORE HOURS"))
            if _hr:
                _hh = _hr.find_parent().p
                if "now open" in _hh.text.lower():
                    _hh = _hr.find_parent().select("p")[1]
                hours = list(_hh.stripped_strings)
            try:
                coord = (
                    sp1.find("a", string=re.compile(r"^VIEW MAP"))["href"]
                    .split("ll=")[1]
                    .split("&")[0]
                    .split(",")
                )
            except:
                try:
                    coord = (
                        sp1.find("a", string=re.compile(r"VIEW MAP"))["href"]
                        .split("/@")[1]
                        .split("/data")[0]
                        .split(",")
                    )
                except:
                    coord = ["", ""]
            yield SgRecord(
                page_url=page_url,
                location_name=link.strong.text.strip(),
                street_address=addr[0],
                city=addr[1].split(",")[0].strip(),
                state=" ".join(addr[1].split(",")[1].strip().split(" ")[:-1]),
                zip_postal=addr[1].split(",")[1].strip().split(" ")[-1].strip(),
                country_code="US",
                phone=addr[-1],
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
