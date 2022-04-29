from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sglogging import SgLogSetup
import re
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgpostal.sgpostal import parse_address_intl

logger = SgLogSetup().get_logger("catchairparty")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://catchairparty.com"
base_url = "https://catchairparty.com/"


def fetch_data():
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        links = soup.select("div.elementor-shortcode select option")
        logger.info(f"{len(links)} found")
        for link in links:
            if not link.get("value"):
                continue
            page_url = link["value"].strip()
            logger.info(page_url)
            sp1 = bs(session.get(page_url, headers=_headers).text, "lxml")
            note = sp1.select_one("section h3")
            if note and "Coming Soon" in note.text:
                continue
            info = sp1.select_one('main section div[data-element_type="column"] h3')
            if info and "store info" not in info.text.lower():
                continue
            marker = sp1.select_one(
                'main section div[data-element_type="column"] ul li'
            )
            raw_address = marker.text.strip()
            addr = parse_address_intl(raw_address + ", United States")
            street_address = addr.street_address_1
            if addr.street_address_2:
                street_address += " " + addr.street_address_2

            try:
                coord = marker.a["href"].split("/@")[1].split("/")[0].split(",")
            except:
                try:
                    coord = marker.a["href"].split("?ll=")[1].split("&")[0].split(",")
                except:
                    coord = ["", ""]

            hours = []
            _hr = sp1.find("", string=re.compile(r"^Store Hours", re.I))
            if _hr:
                hours = list(_hr.find_parent("div").stripped_strings)[2:]
            phone = ""
            if sp1.find("a", href=re.compile(r"tel:")):
                phone = sp1.find("a", href=re.compile(r"tel:")).text.strip()
            yield SgRecord(
                page_url=page_url,
                location_name=link.text.strip(),
                street_address=street_address,
                city=addr.city,
                state=addr.state,
                zip_postal=addr.postcode,
                country_code="US",
                phone=phone,
                latitude=coord[0],
                longitude=coord[1],
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours).replace("–", "-"),
                raw_address=raw_address,
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
